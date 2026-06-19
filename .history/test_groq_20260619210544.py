# test_groq.py

import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('GROQ_API_KEY', '')

if not API_KEY:
    print("❌ GROQ_API_KEY غير موجود في .env")
    exit()

print(f"✅ المفتاح: {API_KEY[:15]}...")

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": "أنت خبير في التحقق من الأخبار. أجب بـ JSON فقط."},
        {"role": "user", "content": "تحقق من هذه المعلومة: أعلنت الحكومة الجزائرية عطلة رسمية."}
    ],
    "temperature": 0.2,
    "max_tokens": 500,
}

req = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    data=json.dumps(payload).encode('utf-8'),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("✅ نجح الطلب!")
        print("\n📝 الرد:")
        print(data['choices'][0]['message']['content'])
except Exception as e:
    print(f"❌ فشل: {e}")