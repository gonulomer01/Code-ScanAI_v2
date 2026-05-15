import google.generativeai as genai

# Kendi API Anahtarını buraya yapıştır
GEMINI_API_KEY = "your_api_key"
genai.configure(api_key=GEMINI_API_KEY)

print("🔍 Google'a bağlanılıyor ve modeller listeleniyor...\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Kullanılabilir Model: {m.name}")
except Exception as e:
    print("Bir hata oluştu:", e)
