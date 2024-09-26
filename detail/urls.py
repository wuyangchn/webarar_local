from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.detail, name="detail_view"),
    path('oven/log', views.lov_view, name="lov_view"),
    path('oven/log/reading', views.experiment_log, name="experiment_log"),
    path('oven/log/updating', views.update_log, name="oven_update_log"),
    path('oven/log/update_oven_log_results', views.update_oven_log_results, name="update_oven_log_results"),
]
