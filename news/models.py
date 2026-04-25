from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='bi-folder')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'


class Article(models.Model):
    VERDICT_CHOICES = [
        ('unverified', 'Non vérifié'),
        ('true', 'Vrai'),
        ('false', 'Faux'),
        ('misleading', 'Trompeur'),
        ('partial', 'Partiellement vrai'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    source_url = models.URLField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, default='unverified')
    verdict_explanation = models.TextField(blank=True)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
