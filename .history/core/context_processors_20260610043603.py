# core/context_processors.py

def language_context(request):
    """
    Context processor to make language available in all templates
    """
    language = request.session.get('language', 'ar')
    
    # Set direction based on language
    direction = 'rtl' if language == 'ar' else 'ltr'
    
    return {
        'LANGUAGE': language,
        'DIRECTION': direction,
    }