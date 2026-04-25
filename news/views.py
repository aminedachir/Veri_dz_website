from django.shortcuts import render, get_object_or_404
from .models import Article, Category


def article_list(request):
    articles = Article.objects.select_related('author', 'category')
    
    category_slug = request.GET.get('category')
    search = request.GET.get('q', '')
    verdict = request.GET.get('verdict', '')

    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    if search:
        articles = articles.filter(title__icontains=search) | articles.filter(content__icontains=search)
    if verdict:
        articles = articles.filter(verdict=verdict)

    categories = Category.objects.all()
    context = {
        'articles': articles,
        'categories': categories,
        'search': search,
        'selected_category': category_slug,
        'selected_verdict': verdict,
    }
    return render(request, 'news/article_list.html', context)


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.views_count += 1
    article.save(update_fields=['views_count'])
    related = Article.objects.filter(category=article.category).exclude(pk=pk)[:3]
    return render(request, 'news/article_detail.html', {'article': article, 'related': related})
