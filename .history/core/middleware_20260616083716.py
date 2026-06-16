# core/middleware.py

from django.utils import translation
from django.conf import settings

class LanguageMiddleware:
    """Middleware to handle language selection from URL or session"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to get language from session
        lang = request.session.get('language')
        if lang and lang in dict(settings.LANGUAGES):
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        else:
            # Default language
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        
        response = self.get_response(request)
        return response