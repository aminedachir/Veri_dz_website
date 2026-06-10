# core/middleware.py

class LanguageMiddleware:
    """
    Middleware to ensure language is always in session
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set default language if not exists
        if 'language' not in request.session:
            request.session['language'] = 'ar'
        
        response = self.get_response(request)
        return response