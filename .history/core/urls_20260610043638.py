# core/urls.py

from django.urls import path
from . import views
from .lang_views import switch_language

urlpatterns = [
    path('', views.home, name='home'),
    path('lang/<str:language_code>/', switch_language, name='switch_language'),
]