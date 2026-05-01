from django.contrib import admin
from .models import Publication
from django.urls import path  # ← Add this import


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_type', 'author', 'created_at', 'is_published', 'views_count')
    list_filter = ('pub_type', 'is_published', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_published',)
    readonly_fields = ('views_count', 'created_at', 'updated_at')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add/', self.admin_site.admin_view(self.redirect_to_frontend), name='publication_add'),
            path('add-image/', self.admin_site.admin_view(self.redirect_to_frontend_image), name='publication_add_image'),
            path('add-video/', self.admin_site.admin_view(self.redirect_to_frontend_video), name='publication_add_video'),
        ]
        return custom_urls + urls
    
    def redirect_to_frontend(self, request):
        """Redirect admin 'add publication' button to frontend form"""
        pub_type = request.GET.get('pub_type', '')
        if pub_type == 'image':
            return redirect('/publications/create/?type=image')
        elif pub_type == 'video':
            return redirect('/publications/create/?type=video')
        else:
            return redirect('/publications/create/')
    
    def redirect_to_frontend_image(self, request):
        """Redirect image publication creation to frontend"""
        return redirect('/publications/create/?type=image')
    
    def redirect_to_frontend_video(self, request):
        """Redirect video publication creation to frontend"""
        return redirect('/publications/create/?type=video')
    
    # Add custom buttons in the changelist page
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_add_buttons'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)
