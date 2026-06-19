# factcheck/groq_service.py

import json
import urllib.request
from django.conf import settings
from .ai_service import (
    SYSTEM_PROMPT,
    _validate_and_fill,
    _extract_json_from_text,
    _demo_response
)


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
    user_content = f"تحقق من صحة هذه المعلومة:\n\n{text}"
    if url:
        user_content += f"\n\nالرابط: {url}"
    
    payload = {
        "model": "llama-3.3-70b-versatile",  # نموذج Groq المجاني
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "max_tokens": 800,
    }
    
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            raw = data['choices'][0]['message']['content'].strip()
            print(f"✅ نجح Groq: llama-3.3-70b-versatile")
            
            try:
                parsed = _extract_json_from_text(raw)
                return _validate_and_fill(parsed)
            except:
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