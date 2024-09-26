from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main_view, name="doc_main_view"),
    path('en', views.doc_en, name="doc_en"),
    path('zh-cn', views.doc_zh_cn, name="doc_zh_cn"),
    path('tutorial', views.tutorial, name="tutorial"),
    path('tutorial/zh-cn', views.tutorial_zh_CN, name="tutorial"),
    path('deploy', views.deploy, name="deploy"),
    path('deploy/zh-cn', views.deploy_zh_CN, name="deploy"),
    path('update_log', views.update_log, name="update_log"),
]
