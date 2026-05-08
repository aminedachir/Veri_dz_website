import json
import urllib.request
import urllib.error
from django.conf import settings


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

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def _fetch_url_content(url: str) -> str:
    """Try to fetch and extract text content from a URL."""
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
            import re
            text = re.sub(r'<script[^>]*>.*?</script>', ' ', raw, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000]
    except Exception:
        return ''


def analyze_with_gemini(text: str, url: str = '') -> dict:
    """Call Google Gemini Flash API to fact-check the given text."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '')

    if not api_key:
        return _demo_response(text, url)

    # Build the user message
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
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_content}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 1000,
            "temperature": 0.2,
        }
    }

    api_url = f"{GEMINI_API_URL}?key={api_key}"

    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            # Extract text from Gemini response structure
            raw = data['candidates'][0]['content']['parts'][0]['text'].strip()
            # Strip markdown code fences if present
            if raw.startswith('```'):
                parts = raw.split('```')
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith('json'):
                    raw = raw[4:]
            result = json.loads(raw.strip())
            return result
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return {'error': 'تجاوزت الحد المسموح به. انتظر دقيقة واحدة ثم أعد المحاولة.'}
        return {'error': f"خطأ HTTP: {e.code}"}
    except urllib.error.URLError as e:
        return {'error': f"خطأ في الشبكة: {str(e)}"}


def _demo_response(text: str, url: str = '') -> dict:
    """Return a demo response when no API key is configured."""
    combined = (text + ' ' + url).lower()

    if any(w in combined for w in ['fake', 'faux', 'mensonge', 'rumeur', 'كذب', 'مزيف', 'شائعة']):
        verdict = 'false'
        confidence = 0.72
        explanation = "يحتوي هذا الادعاء على عدة مؤشرات للتضليل. الصياغة المستخدمة وبنية الرسالة تتطابق مع أنماط المعلومات الكاذبة المنتشرة على الشبكات الاجتماعية."
    elif any(w in combined for w in ['officiel', 'gouvernement', 'ministère', 'aps', 'الحكومة', 'وزارة', 'رسمي']):
        verdict = 'true'
        confidence = 0.81
        explanation = "تبدو هذه المعلومة صادرة عن مصدر رسمي. الصياغة تتسق مع التواصل الحكومي الجزائري المعتاد."
    elif url:
        verdict = 'unverifiable'
        confidence = 0.50
        explanation = "تعذّر جلب محتوى الرابط في وضع التجربة. قم بتهيئة GEMINI_API_KEY للحصول على تحليل حقيقي مع قراءة محتوى الصفحة."
    else:
        verdict = 'unverifiable'
        confidence = 0.55
        explanation = "لا يمكن التحقق من هذا الادعاء دون مصادر إضافية. يُنصح بمراجعة مصادر موثوقة قبل مشاركة هذه المعلومة."

    return {
        "verdict": verdict,
        "confidence_score": confidence,
        "explanation": f"[وضع تجريبي — قم بتهيئة GEMINI_API_KEY للتحليل الحقيقي]\n{explanation}",
        "key_claims": "الادعاء الرئيسي المحدد; السياق الزمني موجود; الجهات المذكورة",
        "red_flags": "المصدر غير محدد; لغة عاطفية مكتشفة" if verdict == 'false' else "",
        "sources_suggested": "وكالة الأنباء الجزائرية (APS); الوطن; TSA الجزائر; إذاعة الجزائر الدولية"
    }