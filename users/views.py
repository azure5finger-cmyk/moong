from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm
from .models import User
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from locations.models import Location


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            location = form.cleaned_data.get("location")

            # ✅ 2단계까지만 있는 지역 자동 보정 (세종 새롬동 케이스)
            if location and not location.eupmyeondong:
                fixed_location = Location.objects.filter(
                    sido=location.sido,
                    sigungu=location.sigungu,
                    eupmyeondong=location.sigungu
                ).first()

                if fixed_location:
                    location = fixed_location

            user.location = location
            user.save()



            print("✅ USER SAVED:", user)
            return redirect("/admin/")   # 임시 확인용
        else:
            print("❌ FORM ERRORS:", form.errors)

    else:
        form = SignupForm()
       
    context = {"form":form}

    return render(request, "users/signup.html", context)