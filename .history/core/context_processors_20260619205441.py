# core/context_processors.py

from django.conf import settings

def language_context(request):
    """Add language-related variables to template context"""
    # ✅ أضف LANGUAGE و LANGUAGE_CODE
    lang = getattr(request, 'LANGUAGE', request.session.get('language', settings.LANGUAGE_CODE))
    return {
        'LANGUAGES': settings.LANGUAGES,
        'LANGUAGE': lang,
        'LANGUAGE_CODE': lang,
    }