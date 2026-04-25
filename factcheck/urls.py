from django.urls import path
from . import views

urlpatterns = [
    path('', views.factcheck_view, name='factcheck'),
    path('history/', views.factcheck_history, name='factcheck_history'),
]
