from django.urls import re_path, path
from . import views

app_name = "moong"

urlpatterns = [
    re_path(r"^$", views.main, name='main'),
    re_path(r'^tags/(?P<tag_name>[^/]+)/$', views.tag_feeds, name='tag_feeds'),
    re_path(r'^post/add/$', views.post_add, name='post_add')     # 테스트 하느라 가상으로 만든 url !!!
]