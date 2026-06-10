# core/lang_views.py

from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@require_POST
def switch_language(request, language_code):
    """
    View to switch language and redirect back
    Languages: ar (Arabic), fr (French), en (English)
    """
    allowed_languages = ['ar', 'fr', 'en']
    
    if language_code in allowed_languages:
        request.session['language'] = language_code
    
    # Redirect back to the previous page
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)