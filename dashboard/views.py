from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from news.models import Article
from factcheck.models import FactCheckResult
from publications.models import Publication
from .forms import ArticleForm


@login_required
def dashboard_home(request):
    user = request.user
    my_articles = Article.objects.filter(author=user).order_by('-created_at')
    my_checks = FactCheckResult.objects.filter(user=user).order_by('-created_at')[:5]

    stats = {
        'total':    my_articles.count(),
        'verified': my_articles.filter(is_verified=True).count(),
        'pending':  my_articles.filter(is_verified=False).count(),
        'views':    sum(a.views_count for a in my_articles),
        'checks':   FactCheckResult.objects.filter(user=user).count(),
    }

    # Admin: load publications data for dashboard widget
    recent_publications = None
    if user.is_staff:
        recent_publications = Publication.objects.order_by('-created_at')[:4]
        stats['publications'] = Publication.objects.count()

    context = {
        'articles':            my_articles[:8],
        'recent_checks':       my_checks,
        'stats':               stats,
        'recent_publications': recent_publications,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def article_create(request):
    if not (request.user.is_journalist or request.user.is_staff):
        messages.error(request, "Seuls les journalistes peuvent publier des articles.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Article soumis avec succès. En attente de vérification.")
            return redirect('dashboard')
    else:
        form = ArticleForm()
    return render(request, 'dashboard/article_form.html', {'form': form, 'action': 'Créer'})


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article modifié avec succès.")
            return redirect('dashboard')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'dashboard/article_form.html', {'form': form, 'article': article, 'action': 'Modifier'})


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        article.delete()
        messages.success(request, "Article supprimé.")
    return redirect('dashboard')