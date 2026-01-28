from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Post, Hashtag, Image
from locations.models import Location
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from django.contrib import messages
from django.http import JsonResponse
import openai
import os
from dotenv import load_dotenv

# OpenAI 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



# 메인 페이지
def main(request):
    # 검색하면 필터링해서 메인페이지에서 바로
    search = request.GET.get('search', '')
    
    if search:
        posts = Post.objects.filter(
            complete=True,
            content__icontains=search
        ).prefetch_related('images', 'hashtags').order_by('-create_time')
    else:
        posts = Post.objects.filter(
            complete=True
        ).prefetch_related('images', 'hashtags').order_by('-create_time')
    
    # 해시태그 리스트
    active_tags = Hashtag.objects.annotate(
        num_posts=Count('posts')
    ).filter(num_posts__gt=0).order_by('-num_posts')
    
    # Location 모델에서 모든 지역 키워드 수집
    location_keywords = set()
    loc_data = Location.objects.values_list('sido', 'sigungu', 'eupmyeondong')
    
    for loc in loc_data:
        for name in filter(None, loc):
            # 1. 원본 추가
            location_keywords.add(name)
            
            # 2. "서울특별시" → "서울"
            clean_name = name.replace('특별시', '').replace('광역시', '').replace('특별자치시', '').replace('특별자치도', '')
            location_keywords.add(clean_name)
            
            # 3. "강남구" → "강남"
            if clean_name.endswith('구'):
                location_keywords.add(clean_name[:-1])
            elif clean_name.endswith('시'):
                location_keywords.add(clean_name[:-1])
            elif clean_name.endswith('군'):
                location_keywords.add(clean_name[:-1])
    
    # 지역 태그와 키워드 태그 구분...
    location_tags = []
    keyword_tags = []
    
    for tag in active_tags:
        # 정확히 일치하거나 부분 일치 확인
        is_location = False
        
        # 정확 일치
        if tag.name in location_keywords:
            is_location = True
        else:
            # 부분 일치
            for loc_keyword in location_keywords:
                if tag.name in loc_keyword or loc_keyword in tag.name:
                    is_location = True
                    break
        
        if is_location:
            location_tags.append(tag)
        else:
            keyword_tags.append(tag)
    
    return render(request, 'moong/main.html', {
        'posts': posts,
        'location_tags': location_tags[:10],  # 상위 10개만
        'keyword_tags': keyword_tags[:10],    # 상위 10개만
        'search': search,
    })



# 해시태그별 게시물 보기
def tag_feeds(request, tag_name):
    posts = Post.objects.filter(
        hashtags__name=tag_name,
        complete=True
    ).prefetch_related('images', 'hashtags').order_by('-create_time')
    
    return render(request, 'moong/tag_feeds.html', {
        'tag_name': tag_name,
        'posts': posts,
    })




# ai 해시태그 쓰려면 pip install openai, pip install python-dotenv 해야합니다!
# .env 파일 manage.py 파일과 같은 곳에 놓고, .env 안에 open ai key 넣으셔야 합니다.
# .gitignore에도 .env 넣어주세욥~
# AI 해시태그 생성 함수
def ai_tags(content, location):
    """내용과 장소를 바탕으로 해시태그 5개 생성"""
    
    if not content and not location:
        return []
    
    prompt = f"""
다음 정보로 SNS 해시태그 6개를 만들어줘.
장소: {location}
내용: {content}

조건:
- # 기호 없이 단어나 명사만 출력
- 쉼표(,)로 구분하고 한글로만 작성
- 장소 해시태그 3개, 내용 해시태그 3개 만들기
- 지역 해시태그는 장소 정보에서 추출하고, 키워드 해시태그는 내용에서 추출
- 키워드 해시태그 예: 맛집, 취미, 친목, 운동 등
- 장소 해시태그 규칙(입력 데이터는 항상 A B C 3단계 형식):
    1. A (광역시/도): 약칭으로 (예: 서울, 세종, 경기, 전북 등)
    2. B (시/군/구): 마지막 글자 제외 (예: 순천, 강남, 의왕 등)
    3. C (읍/면/동): 전체 단어 그대로 (예: 정자동 등)


답변:"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        
        result = response.choices[0].message.content.strip()
        tags = [tag.strip().replace('#', '') for tag in result.split(',') if tag.strip()]
        
        return tags[:6]  # 최대 5개만
        
    except Exception as e:
        print(f"AI 해시태그 생성 오류: {e}")
        return []


# !!!!!!!!로그인 필수
# 임시저장후 ai 해시태그 생성이랑 location 때문에 html이랑 같이 수정했어요.
# 이미지 첨부하는걸 넣었는데 임시저장하고나면 그전에 첨부했던 사진이 날라가네요...
# 임시저장 -> 해시태그 생성, 사진 첨부 다시 하기 -> 게시 하면, 잘 올라가긴 해요.
def post_add(request):
    print("post_add 뷰 호출됨!")
    if request.method == 'POST':
        print("post_add POST 호출됨!")
        form = PostForm(request.POST, request.FILES)
    
        if form.is_valid():
            # Location 찾기
            sido = form.cleaned_data['sido']
            sigungu = form.cleaned_data['sigungu']
            eupmyeondong = form.cleaned_data.get('eupmyeondong', '')
            
            try:
                location = Location.objects.get(
                    sido=sido,
                    sigungu=sigungu,
                    eupmyeondong=eupmyeondong
                )
                location_text = f"{sido} {sigungu} {eupmyeondong}".strip()
            except Location.DoesNotExist:
                messages.error(request, '선택한 지역을 찾을 수 없습니다.')
                return render(request, 'moong/post_add.html', {'form': form})
            
            # 임시저장
            if 'save_temp' in request.POST:
                post = form.save(commit=False)
                post.author = request.user
                post.location = location
                post.complete = False
                post.save()

                # 이미지 저장
                images = request.FILES.getlist('images')
                for index, img_file in enumerate(images):
                    Image.objects.create(post=post, image=img_file, order=index)

                # AI 해시태그
                tags = ai_tags(post.content, location_text)

                messages.success(request, '임시저장 완료!')
                
                # 그냥 form 그대로 넘김 (간단하게)
                return render(request, 'moong/post_add.html', {
                    'form': form,
                    'tags': tags,
                    'temp_post_id': post.id
                })
            
            # 게시
            else:
                temp_post_id = request.POST.get('temp_post_id')
                
                if temp_post_id:
                    # 임시저장된 글
                    post = Post.objects.get(id=temp_post_id, author=request.user)
                    post.complete = True
                    post.save()
                else:
                    # 바로 게시
                    post = form.save(commit=False)
                    post.author = request.user
                    post.location = location
                    post.complete = True
                    post.save()
                    
                    # 이미지 저장
                    images = request.FILES.getlist('images')
                    for index, img_file in enumerate(images):
                        Image.objects.create(post=post, image=img_file, order=index)

                # 해시태그 저장
                selected_tags = request.POST.getlist('tags')
                
                if selected_tags:
                    for tag_name in selected_tags:
                        if tag_name.strip():
                            tag, created = Hashtag.objects.get_or_create(name=tag_name.strip())
                            post.hashtags.add(tag)
                else:
                    tags = ai_tags(post.content, location_text)
                    for tag_name in tags:
                        if tag_name.strip():
                            tag, created = Hashtag.objects.get_or_create(name=tag_name.strip())
                            post.hashtags.add(tag)
                            
                messages.success(request, '게시 완료!')
                return redirect('moong:main')

        else:
            messages.error(request, '입력 확인하세요.')
    else:
        form = PostForm()

    return render(request, 'moong/post_add.html', {'form': form})



def post_list(request):
    """게시글 목록"""
    posts = Post.objects.filter(
        save=True,
        is_cancelled=False
    ).select_related('author', 'location').order_by('-create_time')
    
    return render(request, 'moong/post_list.html', {'posts': posts})


def post_detail(request, post_id):
    """게시글 상세"""
    post = get_object_or_404(
        Post.select_related('author', 'location'),
        id=post_id
    )
    
    return render(request, 'moong/post_detail.html', {'post': post})