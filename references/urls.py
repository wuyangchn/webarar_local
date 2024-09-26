from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.references, name="references_view"),
    path('journal_ranking', views.journal_ranking, name="journal_ranking"),
    path('journal_ranking/callback', views.api_callback, name="api_callback"),
]
