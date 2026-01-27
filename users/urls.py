from django.urls import re_path
from . import views

app_name="users"


urlpatterns = [
    re_path(r"^signup/$", views.signup_view, name="signup")

]
