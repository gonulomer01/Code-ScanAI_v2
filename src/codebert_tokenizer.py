import pandas as pd
from transformers import AutoTokenizer
import os

class CodeBertTokenizer:
    def __init__(self, max_length=512):
        """
        TÜBİTAK İP-1: Kodların CodeBERT vektörlerine dönüştürülmesi.
        microsoft/codebert-base modelinin resmi tokenizer'ı kullanılır.
        """
        print("[SİSTEM] CodeBERT Tokenizer (microsoft/codebert-base) yükleniyor...")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.max_length = max_length # Modelin tek seferde okuyabileceği maksimum kod uzunluğu

    def tokenize_dataset(self, df, code_column="code"):
        """
        Pandas veri çerçevesindeki (DataFrame) kodları alır ve tensör formatına çevirir.
        """
        print(f"[İŞLEM] {len(df)} adet kod parçacığı vektörlere (tensör) dönüştürülüyor...")
        
        # HuggingFace tokenizer'ın toplu (batch) işleme özelliği
        tokenized_output = self.tokenizer(
            df[code_column].tolist(),
            padding="max_length", # Kısa kodları sıfırlarla tamamla (Matris boyutları eşit olmalı)
            truncation=True,      # Çok uzun kodları kes
            max_length=self.max_length,
            return_tensors="pt"   # PyTorch tensörleri (pt) olarak döndür
        )
        
        print("[BAŞARILI] Tokenizasyon işlemi tamamlandı.")
        return tokenized_output

# --- TEST BLOĞU ---
if __name__ == "__main__":
    # 1. Önceki adımda ürettiğimiz örnek veri setini okuyalım
    veri_yolu = "data/raw/sard_mock_data.csv"
    
    if os.path.exists(veri_yolu):
        df = pd.read_csv(veri_yolu)
        
        # 2. Tokenizer'ı başlat ve veriyi işle
        cb_tokenizer = CodeBertTokenizer(max_length=64) # Test için kısa tutuyoruz (64)
        vektorler = cb_tokenizer.tokenize_dataset(df)
        
        # 3. Sonuçları İncele (Makine öğrenmesi verisi neye benzer?)
        print("\n--- Modelin Gireceği Matematiksel Matris (Tensör) ---")
        print("Input IDs (Kelimelerin ID karşılıkları) Boyutu:", vektorler["input_ids"].shape)
        print("Attention Mask (Modelin nereye odaklanacağı) Boyutu:", vektorler["attention_mask"].shape)
        
        print("\n--- İlk Kod Bloğunun Vektör Karşılığı (İlk 15 Sayı) ---")
        # Sadece ilk satırdaki kodun ilk 15 sayısını ekrana basalım
        print(vektorler["input_ids"][0][:15].tolist())
    else:
        print(f"[HATA] Lütfen önce 'data_loader.py' dosyasını çalıştırarak {veri_yolu} dosyasını oluşturun.")