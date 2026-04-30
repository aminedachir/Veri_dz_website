from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    path('', views.publication_list, name='list'),
    path('create/', views.publication_create, name='create'),
    path('manage/', views.publication_manage, name='manage'),
    path('<int:pk>/', views.publication_detail, name='detail'),
    path('<int:pk>/edit/', views.publication_edit, name='edit'),
    path('<int:pk>/delete/', views.publication_delete, name='delete'),
]
