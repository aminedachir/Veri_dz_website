from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from .models import FactCheckResult
from .ai_service import analyze_with_gemini


def _split_semicolons(value: str) -> list:
    """Split a semicolon-separated string into a cleaned list."""
    return [item.strip() for item in value.split(';') if item.strip()]


def factcheck_view(request):
    result = None
    result_data = None
    error = None
    recent_checks = FactCheckResult.objects.all()[:5]

    if request.method == 'POST':
        input_text = request.POST.get('text', '').strip()
        input_url = request.POST.get('url', '').strip()

        if not input_text and not input_url:
            error = "يرجى إدخال نص أو رابط للتحليل."
        elif len(input_text) < 10 and not input_url:
            error = "النص قصير جداً للتحليل الموثوق (10 أحرف على الأقل)."
        else:
            # ✅ التحقق من وجود المفتاح قبل إرسال الطلب
            api_key = getattr(settings, 'GEMINI_API_KEY', '')
            if not api_key:
                error = "⚠️ مفتاح Gemini API غير موجود. يرجى إضافته في متغيرات البيئة."
            else:
                analysis = analyze_with_gemini(input_text, url=input_url)

                if 'error' in analysis:
                    error = analysis['error']
                else:
                    result = FactCheckResult.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        input_text=input_text or input_url,
                        input_url=input_url,
                        verdict=analysis.get('verdict', 'uncertain'),
                        confidence_score=float(analysis.get('confidence_score', 0.5)),
                        explanation=analysis.get('explanation', ''),
                        key_claims=analysis.get('key_claims', ''),
                        red_flags=analysis.get('red_flags', ''),
                        sources_suggested=analysis.get('sources_suggested', ''),
                    )
                    result_data = {
                        'key_claims_list': _split_semicolons(result.key_claims),
                        'red_flags_list':  _split_semicolons(result.red_flags),
                        'sources_list':    _split_semicolons(result.sources_suggested),
                    }

    context = {
        'result':      result,
        'result_data': result_data,
        'error':       error,
        'recent_checks': recent_checks,
        'input_text':  request.POST.get('text', request.GET.get('q', '')),
        'input_url':   request.POST.get('url', request.GET.get('url', '')),
    }
    return render(request, 'factcheck/factcheck.html', context)


def factcheck_history(request):
    checks = FactCheckResult.objects.all()[:50]
    return render(request, 'factcheck/history.html', {'checks': checks})