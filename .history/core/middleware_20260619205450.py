# core/middleware.py

from django.utils import translation
from django.conf import settings

class LanguageMiddleware:
    """Middleware to handle language selection from session"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ✅ احصل على اللغة من الجلسة
        lang = request.session.get('language', settings.LANGUAGE_CODE)
        
        # ✅ تأكد من أن اللغة مدعومة
        if lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE
        
        # ✅ فعّل الترجمة
        translation.activate(lang)
        
        # ✅ أضف اللغة إلى الطلب
        request.LANGUAGE = lang
        request.LANGUAGE_CODE = lang
        
        response = self.get_response(request)
        return response