from django.contrib import admin
from .models import FactCheckResult


@admin.register(FactCheckResult)
class FactCheckResultAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'verdict', 'confidence_score', 'user', 'created_at')
    list_filter = ('verdict',)
    search_fields = ('input_text', 'explanation')
    readonly_fields = ('created_at',)

    def short_text(self, obj):
        return obj.input_text[:80]
    short_text.short_description = 'Texte analysé'
