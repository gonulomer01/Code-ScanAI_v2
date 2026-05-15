import os
import pandas as pd
from datasets import load_dataset

class CodeDataLoader:
    def __init__(self):
        """
        TÜBİTAK İP-1: Gerçek Veri Seti Entegrasyonu.
        HuggingFace üzerinden bulut tabanlı devasa veri setlerini indirir ve işler.
        """
        print("[SİSTEM] Bulut tabanlı Veri Yükleyici (HuggingFace) başlatıldı...")

    def load_huggingface_dataset(self, dataset_name="code_x_glue_cc_defect_detection", sample_size=1000):
        """
        Microsoft CodeXGLUE güvenlik zafiyeti veri setini indirir.
        Bilgisayarı dondurmamak için şimdilik 'sample_size' (örn: 1000 kod) kadarını alır.
        """
        print(f"\n[İŞLEM] ☁️ İnternetten gerçek veri seti çekiliyor: {dataset_name}")
        print("[BİLGİ] Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir...")
        
        try:
            # HuggingFace'ten veri setinin sadece 'train' (eğitim) kısmını indir
            dataset = load_dataset(dataset_name, split="train")
            
            # Veriyi Pandas Tablosuna Çevir
            df = dataset.to_pandas()
            
            # Devasa verinin içinden rastgele 1000 tanesini seç (Hızlı test için)
            df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
            
            # Sütun isimlerini bizim sistemimize (Boru Hattına) uygun hale getir
            # CodeXGLUE'da kodlar 'func', hatalar 'target' olarak adlandırılır.
            df = df.rename(columns={"func": "code", "target": "label"})
            
            # Zafiyet türü sütununu doldur
            df['vulnerability_type'] = df['label'].apply(lambda x: 'Generic_Defect' if x == 1 else 'Safe_Code')
            
            print(f"✅ [BAŞARILI] {len(df)} adet gerçek kaynak kod başarıyla buluttan indirildi!")
            
            # Çok uzun kodları (1000 karakterden uzun) filtrele ki RAM şişmesin
            df = df[df['code'].str.len() < 1000].reset_index(drop=True)
            print(f"🧹 [BİLGİ] Çok uzun kodlar filtrelendi. Kalan net kod sayısı: {len(df)}")
            
            return df

        except Exception as e:
            print(f"❌ [HATA] Veri çekilirken bir sorun oluştu: {e}")
            return None

# --- TEST BLOĞU ---
if __name__ == "__main__":
    loader = CodeDataLoader()
    gercek_veri = loader.load_huggingface_dataset(sample_size=10) # Test için 10 tane çekelim
    if gercek_veri is not None:
        print("\n--- İndirilen Gerçek Veriden 1 Örnek ---")
        print(gercek_veri[['vulnerability_type', 'label']].head(1))