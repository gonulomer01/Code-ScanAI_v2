from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

print("🧠 CodeBERT Beyni Yerel Diskten Yükleniyor...")
# Modelin bulunduğu klasör. Gerekirse "models/fine_tuned_codebert" olarak değiştir.
model_path = "src/fine_tuned_codebert" 

try:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
except Exception as e:
    print(f"❌ MODEL YÜKLENEMEDİ! Yeni model dosyaları doğru klasöre atılmamış olabilir.\nDetay: {e}")
    exit()

# Eğittiğimiz formata TAM UYGUN, include/main içermeyen sinsi bir Buffer Overflow kodu
# Ve yanına eklenmiş sahte ama geçerli bir AST (Ağaç) yapısı
test_code = "void process_user_input(char *user_data) { char safe_buffer[10]; strcpy(safe_buffer, user_data); } <AST_BASLANGICI> function_definition compound_statement call_expression identifier"

inputs = tokenizer(test_code, return_tensors="pt", truncation=True, max_length=256)

with torch.no_grad():
    logits = model(**inputs).logits
    probs = torch.nn.functional.softmax(logits, dim=-1)
    pred = torch.argmax(probs, dim=-1).item()

print("\n" + "="*40)
print(f"Sınıf 0 (Güvenli) Olasılığı: %{probs[0][0].item()*100:.2f}")
print(f"Sınıf 1 (Zafiyetli) Olasılığı: %{probs[0][1].item()*100:.2f}")
print("="*40)

if pred == 1:
    print("🚨 SONUÇ: BEYİN ZAFİYETİ YAKALADI! Ağırlıklar kusursuz.")
    print("-> Teşhis: Modelin çalışıyor ancak Web Arayüzünden (api_service.py) veya AST çıkarıcıdan giden metin bozuluyor.")
else:
    print("✅ SONUÇ: BEYİN GÜVENLİ DEDİ.")
    print("-> Teşhis: Drive'dan indirdiğin yeni model eski klasörün üzerine tam yazılmamış (hala eski modeli okuyor) veya veri setinde sorun var.")