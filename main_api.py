from fastapi import FastAPI
from pydantic import BaseModel
import requests
import re

app = FastAPI(
    title="CodeScanAI YZ Motoru", 
    description="Python YZ Motoru ile C# Arayüzü Arasındaki Köprü",
    version="1.0"
)

class CodeRequest(BaseModel):
    code: str

def extract_clean_code(llm_response: str) -> str:
    # Arayüz çökmesin diye 3 tırnak yazmak yerine `{3} mantığını kullandık!
    match = re.search(r'`{3}(?:csharp)?(.*?)`{3}', llm_response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return llm_response.strip()

@app.post("/scan-and-fix")
def scan_and_fix_code(request: CodeRequest):
    print("\n[SİSTEM] Yeni bir kod analizi talebi geldi!")
    
    prompt = (
        "Sen kıdemli bir siber güvenlik uzmanı ve C# mimarısın. "
        "Aşağıdaki C# kodunda SQL Injection güvenlik açığı var. "
        "SADECE düzeltilmiş, %100 güvenli kodu yaz. Ekstra hiçbir açıklama yazma. "
        "KURALLAR:\n"
        "1. KESİNLİKLE SqlCommand ve Parameters.AddWithValue (Parametreli Sorgu) KULLANMALISIN!\n"
        "2. String birleştirme (+) veya Interpolation ($) KESİNLİKLE KULLANMA!\n"
        "3. Kodu mutlaka 3 adet ters tırnak ve csharp etiketi arasına al.\n\n"
        f"Kod:\n{request.code}"
    )
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            raw_output = response.json()["response"]
            clean_code = extract_clean_code(raw_output)
            
            print("[BAŞARILI] Kod onarıldı ve geri gönderiliyor...")
            
            return {
                "status": "success",
                "original_code": request.code,
                "fixed_code": clean_code
            }
        else:
            return {"status": "error", "message": "Ollama sunucusuna ulaşılamadı."}
            
    except Exception as e:
        return {"status": "error", "message": f"Bir hata oluştu: {str(e)}"}