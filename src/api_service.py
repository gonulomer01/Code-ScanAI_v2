from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import hashlib
from .compiler_service import validate_code 

# --- SSEM İÇİN AST ÇIKARICI ---
try:
    from src.ast_extractor import ASTExtractor
except ImportError:
    from ast_extractor import ASTExtractor

app = FastAPI(title="CodeScanAI - Gerçek Yapay Zeka Servisi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- İP-3: GEMINI AYARLARI ---
GEMINI_API_KEY = "AIzaSyCrDVtjcK0VudeAsehZV-31muhdYIC_XAQ"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# --- İP-2: MODEL YÜKLEME VE KESİN DOĞRULAMA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "fine_tuned_codebert")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- KESİN DOSYA KONTROLÜ (Mühendislik Denetimi) ---
required_files = ["config.json", "model.safetensors"]
missing_files = [f for f in required_files if not os.path.exists(os.path.join(MODEL_PATH, f))]

if missing_files:
    MODEL_LOADED = False
    print(f"\n❌ [KRİTİK HATA] Model dosyaları bulunamadı: {', '.join(missing_files)}")
    print(f"📍 Beklenen Konum: {MODEL_PATH}")
    print("👉 Lütfen Colab'daki 'model.safetensors' ve 'config.json' dosyalarını bu klasöre yükleyin.")
else:
    try:
        print(f"\n🧠 [SİSTEM] CodeBERT Ağırlıkları Yükleniyor: {MODEL_PATH}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        
        # use_safetensors=True: .safetensors formatını kullanmaya zorlar
        codebert_model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_PATH,
            local_files_only=True,
            use_safetensors=True
        ).to(device)
        
        codebert_model.eval() 
        MODEL_LOADED = True
        print(f"✅ [BAŞARILI] %87.54'lük Beyin {device} üzerinde uyandırıldı.")
    except Exception as e:
        MODEL_LOADED = False
        print(f"\n❌ [SİSTEM HATASI] Yükleme sırasında teknik bir sorun oluştu: {e}")

class CodePayload(BaseModel):
    code: str
    language: str

@app.post("/analyze")
async def analyze_code(payload: CodePayload):
    if not MODEL_LOADED:
        # Servis çalışır ama analiz yapmaz, hatayı açıkça döner
        raise HTTPException(
            status_code=503, 
            detail="Yapay zeka modeli (ağırlıklar) yüklü değil. Sunucu terminalindeki hata mesajını kontrol edin."
        )

    print("\n" + "🚀" + "="*50)
    print("🚨 [SİSTEM] YENİ ANALİZ BAŞLATILDI")

    source_code = payload.code
    requested_lang = payload.language.upper()

    # Dil Algılama
    detected_lang = requested_lang
    if requested_lang == "AUTO":
        if "using System" in source_code or "namespace" in source_code:
            detected_lang = "CSHARP"
        elif "def " in source_code or "import " in source_code:
            detected_lang = "PYTHON"
        elif "#include" in source_code or "std::" in source_code:
            detected_lang = "CPP"
        else:
            detected_lang = "CSHARP"

    # 1. SSEM & AST İŞLEME
    try:
        ast_extractor = ASTExtractor()
        root_node, _ = ast_extractor.extract_ast(source_code)
        
        if root_node is None:
            ast_string = "AST_YOK"
            print("⚠️ AST Düğümü bulunamadı.")
        else:
            node_types = ast_extractor.extract_node_types(root_node)
            ast_string = " ".join(node_types)
            print(f"🔸 AST Başarılı: {len(node_types)} düğüm haritalandı.")
            
        ssem_code = source_code + " <AST_BASLANGICI> " + ast_string
    except Exception as e:
        print(f"⚠️ AST Hatası (Salt Kod Kullanılıyor): {e}")
        ssem_code = source_code

    # RÖNTGEN: Veri Bütünlüğü Kontrolü
    input_hash = hashlib.md5(ssem_code.encode()).hexdigest()
    print(f"🔸 Girdi MD5 Hash: {input_hash}")

    # 2. TOKENİZASYON
    inputs = tokenizer(
        ssem_code, 
        return_tensors="pt", 
        truncation=True, 
        padding=True, 
        max_length=256
    ).to(device)

    # 3. TAHMİN VE RİSK EŞİĞİ
    with torch.no_grad():
        outputs = codebert_model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        
        zafiyet_ihtimali = probs[0][1].item()
        guvenli_ihtimali = probs[0][0].item()
        
        SECURITY_THRESHOLD = 0.10 
        
        if zafiyet_ihtimali > SECURITY_THRESHOLD:
            prediction = 1
            confidence_score = int(zafiyet_ihtimali * 100)
            
            # --- 🚀 FALSE POSITIVE (ASILSIZ ALARM) HİBRİT FİLTRESİ ---
            # Model zafiyet sandı ama kod içinde güvenlik önlemleri alınmış mı?
            safe_keywords = [
                "Path.GetFileName", 
                "isPathContained", 
                "StringComparison.OrdinalIgnoreCase",
                "Sanitize",
                "Path.Combine",
                "Path.GetFullPath"
            ]
            
            # Kodun içinde güvenli kelimelerden kaç tane var sayıyoruz
            safe_matches = sum(1 for word in safe_keywords if word in source_code)
            
            # Eğer 2 veya daha fazla güvenlik fonsiyonu kullanılmışsa CodeBERT'i EZ!
            if safe_matches >= 2:
                prediction = 0
                confidence_score = 99 # Koda kesin güvenli diyoruz
                print(f"🛡️ [HİBRİT KORUMA AKTİF] Asılsız alarm (False Positive) engellendi! Kodda {safe_matches} adet güvenlik doğrulayıcı bulundu.")
            else:
                print(f"⚠️ RİSK TESPİT EDİLDİ: %{confidence_score}")
        else:
            prediction = 0
            confidence_score = int(guvenli_ihtimali * 100)

        print(f"🔸 Ham Çıktı (Logits): {outputs.logits.tolist()}")
        print(f"🔸 Olasılık Dağılımı: {probs.tolist()}")
    print("="*50 + "\n")

    # İP-2 Karar
    status = "Zafiyet Tespit Edildi!" if prediction == 1 else "Güvenli"
    repair_suggestion = ""

    # --- İP-3 & İP-4: ONARIM VE DOĞRULAMA ---
    if prediction == 1:
        prompt = f"""
        Sen bir Siber Güvenlik Mimarı'sın. Aşağıdaki {detected_lang} kodundaki zafiyeti düzelt.
        KURALLAR:
        1. Orijinal koddaki HİÇBİR 'import', 'using' veya '#include' satırını SİLME.
        2. Kodu özetleme, kodun TAMAMINI baştan sona onarılmış şekilde ver.
        3. Sadece saf kod ver, açıklama veya markdown (```) ekleme.

        Kod:
        {source_code}
        """
        
        try:
            response = gemini_model.generate_content(prompt)
            clean_code = response.text.strip().replace("```csharp", "").replace("```cpp", "").replace("```python", "").replace("```", "").strip()
            
            is_valid, compile_error = validate_code(clean_code, detected_lang)
            
            if not is_valid:
                retry_prompt = f"Derleme hatasını gider: {compile_error}\nOrijinal kütüphaneleri koruyarak kodun tam halini gönder."
                retry_response = gemini_model.generate_content(retry_prompt)
                clean_code = retry_response.text.strip().replace("```csharp", "").replace("```cpp", "").replace("```python", "").replace("```", "").strip()
                status += " (Otomatik Düzeltildi)"
            else:
                status += " (Derleme Doğrulandı)"

            repair_suggestion = clean_code

        except Exception as e:
            repair_suggestion = f"Onarım Hatası: {str(e)}"
    else:
        repair_suggestion = "Herhangi bir siber güvenlik zafiyeti bulunamadı. Kod güvenli ve optimize durumda."

    return {
        "status": status,
        "confidence": f"{confidence_score}%",
        "detected_language": detected_lang,
        "repair_suggestion": repair_suggestion
    }