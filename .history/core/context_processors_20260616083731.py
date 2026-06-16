# core/context_processors.py

from django.conf import settings

def language_context(request):
    """Add language-related variables to template context"""
    return {
        'LANGUAGES': settings.LANGUAGES,
        'LANGUAGE_CODE': getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE),
    }