import json
import re
import urllib.request
import urllib.error
from django.conf import settings


# ---------------------------------------------------------------------------
# نظام التصنيف الجديد
# ---------------------------------------------------------------------------

VALID_VERDICTS = {"trusted", "no_evidence", "uncertain", "conflicting"}

VERDICT_LABELS = {
    "trusted":     "موثوق جداً",
    "no_evidence": "لا يوجد أدلة كافية",
    "uncertain":   "غير مؤكد",
    "conflicting": "مصادر متعارضة",
}

# تحويل قيم Gemini القديمة → الجديدة
LEGACY_VERDICT_MAP = {
    "true":         "trusted",
    "false":        "no_evidence",
    "misleading":   "conflicting",
    "partial":      "uncertain",
    "unverifiable": "uncertain",
}

SYSTEM_PROMPT = """أنت خبير متخصص في التحقق من الأخبار والمعلومات (fact-checking) في السياق الجزائري والمغاربي.
مهمتك هي تحليل النصوص والادعاءات وتحديد مدى صحتها بدقة عالية.

قواعد صارمة يجب الالتزام بها:
- إذا كانت المعلومة صحيحة وموثقة → verdict: "true"
- إذا كانت المعلومة كاذبة أو مزيفة → verdict: "false"
- إذا كانت مضللة (جزئياً صحيحة لكن تُقدَّم بطريقة خاطئة) → verdict: "misleading"
- إذا كانت جزئياً صحيحة وتحتاج تفصيلاً → verdict: "partial"
- إذا كان من المستحيل التحقق منها → verdict: "unverifiable"

كن صارماً وموضوعياً. لا تتساهل في إعطاء حكم "true" إلا إذا كنت متأكداً تماماً.
لا تتردد في إعطاء حكم "false" إذا كانت المعلومة واضحة الكذب.

أجب دائماً بـ JSON صحيح فقط بهذا الهيكل بالضبط (بدون أي نص خارج JSON):
{
  "verdict": "true" | "false" | "misleading" | "partial" | "unverifiable",
  "confidence_score": 0.0-1.0,
  "explanation": "شرح مفصل بالعربية (2-4 جمل) يوضح سبب الحكم",
  "key_claims": "الادعاءات الرئيسية المحددة (مفصولة بفاصلة منقوطة)",
  "red_flags": "مؤشرات التضليل المكتشفة (مفصولة بفاصلة منقوطة، فارغة إذا لم توجد)",
  "sources_suggested": "المصادر الموصى بها للتحقق (مفصولة بفاصلة منقوطة)"
}"""

# ✅ استخدام نموذج يدعم مفاتيح AQ.
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

REQUIRED_FIELDS = {
    "verdict":           "uncertain",
    "confidence_score":  0.5,
    "explanation":       "",
    "key_claims":        "",
    "red_flags":         "",
    "sources_suggested": "",
}


# ---------------------------------------------------------------------------
# تحويل verdict
# ---------------------------------------------------------------------------

def _normalize_verdict(raw_verdict: str) -> str:
    """يحوّل قيمة verdict (قديمة أو جديدة) إلى إحدى القيم الأربع الجديدة."""
    v = str(raw_verdict).strip().lower()
    if v in VALID_VERDICTS:
        return v
    return LEGACY_VERDICT_MAP.get(v, "uncertain")


# ---------------------------------------------------------------------------
# استخراج JSON من النص
# ---------------------------------------------------------------------------

def _extract_json_from_text(raw: str) -> dict:
    if not raw or not raw.strip():
        raise ValueError("الرد فارغ")

    text = _strip_markdown_fences(raw.strip())

    result = _try_parse(text)
    if result is not None:
        return result

    extracted = _find_json_object(text)
    if extracted is not None:
        result = _try_parse(extracted)
        if result is not None:
            return result
        fixed = _fix_incomplete_json(extracted)
        result = _try_parse(fixed)
        if result is not None:
            return result

    fixed = _fix_incomplete_json(text)
    result = _try_parse(fixed)
    if result is not None:
        return result

    raise ValueError(f"تعذّر استخراج JSON صالح من الرد: {raw[:200]!r}")


def _strip_markdown_fences(text: str) -> str:
    match = re.compile(r'^```(?:json)?\s*\n?(.*?)\n?```\s*$', re.DOTALL).search(text)
    if match:
        return match.group(1).strip()
    text = re.sub(r'^```(?:json)?\s*', '', text).strip()
    text = re.sub(r'```\s*$', '', text).strip()
    return text


def _find_json_object(text: str) -> str | None:
    start = text.find('{')
    if start == -1:
        return None
    end = text.rfind('}')
    if end == -1 or end <= start:
        return text[start:]
    return text[start:end + 1]


def _fix_incomplete_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r',\s*([}\]])', r'\1', text)

    count = 0
    i = 0
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == '"':
            count += 1
        i += 1
    if count % 2 != 0:
        text += '"'

    text += ']' * max(0, text.count('[') - text.count(']'))
    text += '}' * max(0, text.count('{') - text.count('}'))
    return text


def _try_parse(text: str) -> dict | None:
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    return None


# ---------------------------------------------------------------------------
# التحقق من صحة البنية وتعبئة القيم الافتراضية
# ---------------------------------------------------------------------------

def _validate_and_fill(data: dict) -> dict:
    result = {}
    for field, default in REQUIRED_FIELDS.items():
        value = data.get(field, default)
        result[field] = value if value is not None else default

    result["verdict"] = _normalize_verdict(result["verdict"])

    try:
        score = float(result["confidence_score"])
        result["confidence_score"] = max(0.0, min(1.0, score))
    except (TypeError, ValueError):
        result["confidence_score"] = 0.5

    for field in ("explanation", "key_claims", "red_flags", "sources_suggested"):
        if not isinstance(result[field], str):
            result[field] = str(result[field]) if result[field] else ""

    return result


# ---------------------------------------------------------------------------
# جلب محتوى URL
# ---------------------------------------------------------------------------

def _fetch_url_content(url: str) -> str:
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; FactCheckBot/1.0)',
                'Accept': 'text/html,application/xhtml+xml,*/*',
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read(50000).decode('utf-8', errors='ignore')
            text = re.sub(r'<script[^>]*>.*?</script>', ' ', raw, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000]
    except Exception:
        return ''


# ---------------------------------------------------------------------------
# الدالة الرئيسية (معدلة لدعم مفاتيح AQ.)
# ---------------------------------------------------------------------------

def analyze_with_gemini(text: str, url: str = '') -> dict:
    api_key = getattr(settings, 'GEMINI_API_KEY', '')

    if not api_key:
        return _demo_response(text, url)

    user_content = "تحقق من صحة هذه المعلومة:\n\n"

    if url:
        user_content += f"الرابط: {url}\n\n"
        fetched = _fetch_url_content(url)
        if fetched:
            user_content += f"محتوى الصفحة:\n{fetched}\n\n"
        else:
            user_content += "(تعذّر جلب محتوى الصفحة — سيتم التحقق من الرابط فقط)\n\n"

    if text:
        user_content += f"النص:\n{text}"

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_content}]}],
        "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.2},
    }

    # ✅ الطريقة الجديدة: إرسال المفتاح في Header بدلاً من URL
    req = urllib.request.Request(
        GEMINI_API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "X-Goog-API-Key": api_key,  # ✅ المفتاح هنا (يدعم AQ.)
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            raw = data['candidates'][0]['content']['parts'][0]['text'].strip()
            parsed = _extract_json_from_text(raw)
            return _validate_and_fill(parsed)

    except urllib.error.HTTPError as e:
        # ✅ قراءة تفاصيل الخطأ بشكل أفضل
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            error_message = error_data.get('error', {}).get('message', str(e))
        except:
            error_message = str(e)
        
        if e.code == 429:
            return {'error': 'تجاوزت الحد المسموح به. انتظر دقيقة واحدة ثم أعد المحاولة.'}
        elif e.code == 403:
            return {'error': f'❌ خطأ 403: المفتاح غير صالح أو غير مفعل. تأكد من مفتاح Gemini API.'}
        elif e.code == 400:
            return {'error': f'❌ خطأ 400: طلب غير صحيح. {error_message}'}
        else:
            return {'error': f"خطأ HTTP {e.code}: {error_message}"}
            
    except urllib.error.URLError as e:
        return {'error': f"خطأ في الشبكة: {str(e)}"}
    except (KeyError, IndexError) as e:
        return {'error': f"بنية استجابة Gemini غير متوقعة: {str(e)}"}
    except ValueError as e:
        return _fallback_response(str(e))


# ---------------------------------------------------------------------------
# الردود الاحتياطية
# ---------------------------------------------------------------------------

def _fallback_response(reason: str = '') -> dict:
    return _validate_and_fill({
        "verdict": "uncertain",
        "confidence_score": 0.0,
        "explanation": (
            "تعذّر تحليل رد نموذج الذكاء الاصطناعي بسبب خطأ في التنسيق. "
            "يُرجى إعادة المحاولة أو تبسيط النص المُدخل."
            + (f" (السبب التقني: {reason})" if reason else "")
        ),
        "key_claims": "",
        "red_flags": "",
        "sources_suggested": "وكالة الأنباء الجزائرية (APS); الوطن; TSA الجزائر",
    })


def _demo_response(text: str, url: str = '') -> dict:
    combined = (text + ' ' + url).lower()

    if any(w in combined for w in ['fake', 'faux', 'mensonge', 'rumeur', 'كذب', 'مزيف', 'شائعة']):
        verdict, confidence = 'no_evidence', 0.72
        explanation = "يحتوي هذا الادعاء على عدة مؤشرات للتضليل. الصياغة المستخدمة وبنية الرسالة تتطابق مع أنماط المعلومات الكاذبة المنتشرة على الشبكات الاجتماعية."
        red_flags = "المصدر غير محدد; لغة عاطفية مكتشفة"
    elif any(w in combined for w in ['officiel', 'gouvernement', 'ministère', 'aps', 'الحكومة', 'وزارة', 'رسمي']):
        verdict, confidence = 'trusted', 0.81
        explanation = "تبدو هذه المعلومة صادرة عن مصدر رسمي. الصياغة تتسق مع التواصل الحكومي الجزائري المعتاد."
        red_flags = ""
    elif url:
        verdict, confidence = 'uncertain', 0.50
        explanation = "تعذّر جلب محتوى الرابط في وضع التجربة. قم بتهيئة GEMINI_API_KEY للحصول على تحليل حقيقي."
        red_flags = ""
    else:
        verdict, confidence = 'uncertain', 0.55
        explanation = "لا يمكن التحقق من هذا الادعاء دون مصادر إضافية. يُنصح بمراجعة مصادر موثوقة قبل مشاركة هذه المعلومة."
        red_flags = ""

    return _validate_and_fill({
        "verdict": verdict,
        "confidence_score": confidence,
        "explanation": f"[وضع تجريبي — قم بتهيئة GEMINI_API_KEY للتحليل الحقيقي]\n{explanation}",
        "key_claims": "الادعاء الرئيسي المحدد; السياق الزمني موجود; الجهات المذكورة",
        "red_flags": red_flags,
        "sources_suggested": "وكالة الأنباء الجزائرية (APS); الوطن; TSA الجزائر; إذاعة الجزائر الدولية",
    })