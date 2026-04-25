from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import FactCheckResult
from .ai_service import analyze_with_claude


def factcheck_view(request):
    result = None
    error = None
    recent_checks = FactCheckResult.objects.all()[:5]

    if request.method == 'POST':
        input_text = request.POST.get('text', '').strip()
        input_url = request.POST.get('url', '').strip()

        if not input_text and not input_url:
            error = "Veuillez saisir un texte ou une URL à analyser."
        elif len(input_text) < 10 and not input_url:
            error = "Le texte est trop court pour une analyse fiable (minimum 10 caractères)."
        else:
            analysis = analyze_with_claude(input_text or input_url, url=input_url)

            if 'error' in analysis:
                error = analysis['error']
            else:
                result = FactCheckResult.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    input_text=input_text or input_url,
                    input_url=input_url,
                    verdict=analysis.get('verdict', 'unverifiable'),
                    confidence_score=float(analysis.get('confidence_score', 0.5)),
                    explanation=analysis.get('explanation', ''),
                    key_claims=analysis.get('key_claims', ''),
                    red_flags=analysis.get('red_flags', ''),
                    sources_suggested=analysis.get('sources_suggested', ''),
                )

    context = {
        'result': result,
        'error': error,
        'recent_checks': recent_checks,
        'input_text': request.POST.get('text', request.GET.get('q', '')),
        'input_url': request.POST.get('url', request.GET.get('url', '')),
    }
    return render(request, 'factcheck/factcheck.html', context)


def factcheck_history(request):
    checks = FactCheckResult.objects.all()[:50]
    return render(request, 'factcheck/history.html', {'checks': checks})
