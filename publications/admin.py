from django.contrib import admin
from .models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_type', 'author', 'created_at', 'is_published', 'views_count')
    list_filter = ('pub_type', 'is_published', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_published',)
    readonly_fields = ('views_count', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)
