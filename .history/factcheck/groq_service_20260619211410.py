# factcheck/groq_service.py

import json
import urllib.request
from django.conf import settings
from .ai_service import (
    _validate_and_fill,
    _extract_json_from_text,
    _demo_response
)

# ✅ SYSTEM_PROMPT مخصص لـ Groq يطلب JSON صريحاً
GROQ_SYSTEM_PROMPT = """أنت خبير متخصص في التحقق من الأخبار والمعلومات في السياق الجزائري.
مهمتك هي تحليل النصوص وتحديد مدى صحتها.

⚠️ **هام جداً:** أجب فقط بـ JSON صحيح، ولا تكتب أي شيء خارج JSON.

الهيكل المطلوب:
{
  "verdict": "trusted" | "no_evidence" | "uncertain" | "conflicting",
  "confidence_score": 0.0-1.0,
  "explanation": "شرح مفصل بالعربية (2-4 جمل)",
  "key_claims": "الادعاءات الرئيسية (مفصولة بفاصلة منقوطة)",
  "red_flags": "مؤشرات التضليل (مفصولة بفاصلة منقوطة، فارغة إذا لم توجد)",
  "sources_suggested": "المصادر الموصى بها (مفصولة بفاصلة منقوطة)"
}

معنى الأحكام:
- "trusted": المعلومة صحيحة وموثقة من مصادر رسمية
- "no_evidence": لا يوجد أدلة كافية تدعم الادعاء
- "uncertain": لا يمكن الجزم بصحة المعلومة
- "conflicting": المصادر متعارضة حول هذه المعلومة

مثال على الرد الصحيح:
{
  "verdict": "trusted",
  "confidence_score": 0.85,
  "explanation": "هذه المعلومة صحيحة لأنها صادرة عن وزارة الداخلية الجزائرية.",
  "key_claims": "عطلة رسمية; رأس السنة الأمازيغية; 12 يناير",
  "red_flags": "",
  "sources_suggested": "وزارة الداخلية; وكالة الأنباء الجزائرية APS"
}"""


def analyze_with_groq(text: str, url: str = '') -> dict:
    """
    استخدام Groq API للتحقق من الأخبار
    - سريع جداً (معالجات LPU)
    - مجاني
    - مستقر
    """
    
    api_key = getattr(settings, 'GROQ_API_KEY', '')
    
    if not api_key:
        return _demo_response(text, url)
    
    # بناء المحتوى
    user_content = f"تحقق من صحة هذه المعلومة وأعطني JSON فقط:\n\n{text}"
    if url:
        user_content += f"\n\nالرابط: {url}"
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": GROQ_SYSTEM_PROMPT},  # ✅ Prompt مخصص
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1,  # ✅ درجة حرارة منخفضة للحصول على JSON دقيق
        "max_tokens": 800,
        "response_format": {"type": "json_object"},  # ✅ يطلب JSON من Groq
    }
    
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (compatible; VeriDZ/1.0)",  # ✅ أضف User-Agent
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            raw = data['choices'][0]['message']['content'].strip()
            print(f"✅ نجح Groq: llama-3.3-70b-versatile")
            print(f"📝 الرد الخام: {raw[:200]}...")  # ✅ للتصحيح
            
            try:
                parsed = _extract_json_from_text(raw)
                return _validate_and_fill(parsed)
            except Exception as e:
                print(f"⚠️ فشل استخراج JSON: {e}")
                # إذا لم يكن JSON، أعد النص كشرح
                return {
                    "verdict": "uncertain",
                    "confidence_score": 0.5,
                    "explanation": raw[:500],
                    "key_claims": "",
                    "red_flags": "",
                    "sources_suggested": "",
                }
                
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            error_message = error_data.get('error', {}).get('message', str(e))
        except:
            error_message = str(e)
        
        if e.code == 429:
            return {'error': 'تجاوزت الحد المسموح به في Groq. انتظر ثم أعد المحاولة.'}
        elif e.code == 401:
            return {'error': '❌ خطأ 401: مفتاح Groq غير صالح. تأكد من المفتاح في البيئة.'}
        else:
            return {'error': f"خطأ في Groq ({e.code}): {error_message}"}
            
    except Exception as e:
        return {'error': f"خطأ في Groq: {str(e)}"}