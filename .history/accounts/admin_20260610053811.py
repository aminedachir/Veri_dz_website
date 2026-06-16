from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_journalist', 'is_media_organization', 'is_staff', 'date_joined')
    list_filter = ('is_journalist', 'is_media_organization', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('VeriDz', {'fields': ('is_journalist', 'is_media_organization', 'bio', 'organization', 'avatar')}),
    )
    search_fields = ('username', 'email', 'organization')