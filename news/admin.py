from django.contrib import admin
from .models import Article, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_verified', 'verdict', 'created_at', 'views_count')
    list_filter = ('is_verified', 'verdict', 'category')
    search_fields = ('title', 'content', 'author__username')
    list_editable = ('is_verified', 'verdict')
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    fieldsets = (
        ('Contenu', {'fields': ('title', 'content', 'source_url', 'image', 'author', 'category')}),
        ('Vérification', {'fields': ('is_verified', 'verdict', 'verdict_explanation')}),
        ('Statistiques', {'fields': ('views_count', 'created_at', 'updated_at')}),
    )
