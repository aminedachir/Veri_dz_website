from django.shortcuts import render
from news.models import Article


def home(request):
    featured = Article.objects.filter(is_verified=True).order_by('-created_at')[:6]
    latest = Article.objects.order_by('-created_at')[:3]
    context = {
        'featured': featured,
        'latest': latest,
    }
    return render(request, 'core/home.html', context)