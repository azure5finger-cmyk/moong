from django import forms
from .models import Post
from locations.models import Location

class PostForm(forms.ModelForm):

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(), 
        # forms.py 실행시에는 빈queryset호출
        # queryset : DB와 연결 되어 DB에 실제로 존재하는 선택지만 허용
        # ModelChoiceField + queryset를 사용(ChoiceField와의 차이점)
        label="모임 지역 선택",
        widget=forms.Select(attrs={"class" : "form-select"}), 
        required=False,
    )
    class Meta:
        model = Post
        fields = [
            'title', 
            'content',
            'moim_date', 
            'moim_time',
            'max_people',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '내용을 입력하세요'
            }) ,
            'moim_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type' : 'date'
            }) , 
            'moim_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type' : 'time'
            }),
            'max_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '최대 인원(선택)',
                'min' : 2
            }),
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'moim_date': '날짜',
            'moim_time': '시간',
            'max_people': '최대 인원',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        location_id = self.data.get("location")
        if location_id:
            self.fields["location"].queryset = Location.objects.filter(
                id=location_id
            )
        # # 시/도 선택지 설정
        # sido_list = Location.objects.values_list('sido', flat=True).distinct().order_by('sido')
        # self.fields['sido'].widget.choices = [('', '시/도 선택')] + [(sido, sido) for sido in sido_list]
        
        # # 초기값이 있으면 (수정 시)
        # if self.instance.pk and self.instance.location:
        #     self.fields['sido'].initial = self.instance.location.sido
        #     self.fields['sigungu'].initial = self.instance.location.sigungu
        #     self.fields['eupmyeondong'].initial = self.instance.location.eupmyeondong
            
        #     # 시/군/구 선택지
        #     sigungu_list = Location.objects.filter(
        #         sido=self.instance.location.sido
        #     ).values_list('sigungu', flat=True).distinct().order_by('sigungu')
        #     self.fields['sigungu'].widget.choices = [('', '시/군/구 선택')] + [(sg, sg) for sg in sigungu_list]
            
        #     # 읍/면/동 선택지
        #     eupmyeondong_list = Location.objects.filter(
        #         sido=self.instance.location.sido,
        #         sigungu=self.instance.location.sigungu
        #     ).values_list('eupmyeondong', flat=True).distinct().order_by('eupmyeondong')
        #     self.fields['eupmyeondong'].widget.choices = [('', '읍/면/동 선택')] + [(emd, emd) for emd in eupmyeondong_list]
        # else:
        #     # 신규 작성 시
        #     self.fields['sigungu'].widget.choices = [('', '시/도를 먼저 선택하세요')]
        #     self.fields['eupmyeondong'].widget.choices = [('', '시/군/구를 먼저 선택하세요')]