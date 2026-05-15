import pandas as pd
import os

print("📂 [SİSTEM] İşlenmiş Veri Seti (.pkl) Yükleniyor...\n")

dosya_yolu = "data/processed/processed_dataset.pkl"
df = pd.read_pickle(dosya_yolu)

# 1. İNSAN OKUNABİLİR TEMİZ CSV (Değişmedi, aynı kalıyor)
csv_yolu = "data/processed/insan_okunabilir_veri.csv"
df_temiz = df.drop(columns=['input_ids', 'attention_mask'])
df_temiz.to_csv(csv_yolu, index=False, sep=';', encoding='utf-8-sig')
print(f"💾 [BAŞARILI] Excel tablosu güncellendi: {csv_yolu}")

# 2. HOCA İÇİN TÜM KODLARI İÇEREN DETAYLI METİN (TXT) RAPORU
txt_yolu = "data/processed/ornek_kod_raporu.txt"
with open(txt_yolu, "w", encoding="utf-8") as f:
    f.write("=== CODE-SCANAI YAPAY ZEKA VERİ İŞLEME RAPORU (İP-1) ===\n\n")
    f.write(f"Toplam Kayıt Sayısı: {len(df)}\n")
    f.write(f"Sütunlar: {list(df.columns)}\n\n")
    f.write("=" * 60 + "\n\n")
    
    # Tüm satırları (kodları) tek tek dönen döngü
    for index, row in df.iterrows():
        f.write(f"--- {index + 1}. KOD ÖRNEĞİNİN TAM DETAYI ---\n\n")
        
        f.write("🔸 ORİJİNAL KODUN TAMAMI:\n")
        f.write("-" * 50 + "\n")
        f.write(f"{row['code']}\n")
        f.write("-" * 50 + "\n\n")
        
        f.write(f"🔸 ZAFİYET TÜRÜ: {row['vulnerability_type']}\n")
        f.write(f"🔸 HATA ETİKETİ (1=Hatalı, 0=Temiz): {row['label']}\n\n")
        
        f.write("🔸 ÇIKARILAN AST YAPISI (İlk 20 Düğüm):\n")
        f.write(f"{row['ast_features'].split()[:20]}...\n\n")
        
        f.write("🔸 CODEBERT VEKTÖRLERİ (İlk 30 Tensör ID'si):\n")
        f.write(f"{row['input_ids'][:30]}...\n\n")
        
        f.write("=" * 60 + "\n\n") # Her kod arasına ayırıcı çizgi

print(f"📄 [BAŞARILI] {len(df)} kodun tamamını içeren detaylı metin raporu oluşturuldu: {txt_yolu}")
print("\n✅ İşlem bitti! Lütfen TXT dosyasını açıp 4 kodun da alt alta listelendiğini teyit edin.")