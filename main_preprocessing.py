import os
import pandas as pd
from sklearn.utils import resample  # Veri dengeleme (Oversampling) için
from src.data_loader import CodeDataLoader
from src.ast_extractor import ASTExtractor
from src.codebert_tokenizer import CodeBertTokenizer

def run_pipeline():
    print("🚀 [BAŞLANGIÇ] Code-ScanAI Veri Ön İşleme (SSEM + Oversampling) Başlıyor...\n")

    # 1. VERİ YÜKLEME AŞAMASI
    print("[ADIM 1] Gerçek Veri Yükleniyor (HuggingFace / CodeXGLUE)...")
    loader = CodeDataLoader()
    df = loader.load_huggingface_dataset(sample_size=10000) 

    if df is None:
        return

    # --- EKLENEN: VERİ DENGELEME (OVERSAMPLING) ---
    print("\n[ADIM 1.5] Sınıf Dengesizliği Gideriliyor (Oversampling)...")
    df_temiz = df[df['label'] == 0]
    df_hatali = df[df['label'] == 1]
    
    print(f"Orijinal Dağılım -> Temiz: {len(df_temiz)}, Hatalı: {len(df_hatali)}")
    
    if len(df_hatali) < len(df_temiz) and len(df_hatali) > 0:
        # Hatalı kodları, temiz kod sayısına ulaşana kadar sentetik olarak artırıyoruz
        df_hatali_artirilmis = resample(df_hatali, 
                                        replace=True,     
                                        n_samples=len(df_temiz), 
                                        random_state=42)
        df = pd.concat([df_temiz, df_hatali_artirilmis])
        df = df.sample(frac=1, random_state=42).reset_index(drop=True) # Karıştır
        print(f"✅ Yeni Dengeli Dağılım -> Temiz: {len(df[df['label']==0])}, Hatalı: {len(df[df['label']==1])}")

    # 2. YAPISAL ANALİZ VE SSEM (STRUCTURAL SEMANTIC ENHANCEMENT)
    print("\n[ADIM 2] Kodların AST Yapısı Çıkarılıyor ve Kod ile Birleştiriliyor (SSEM)...")
    ast_extractor = ASTExtractor()
    ssem_codes = []

    for index, row in df.iterrows():
        code = row['code']
        root_node, detected_lang = ast_extractor.extract_ast(code)
        node_types = ast_extractor.extract_node_types(root_node)
        ast_string = " ".join(node_types)
        
        # KRİTİK NOKTA: Kodu ve AST yapısını yapay zeka için tek bir metinde birleştiriyoruz.
        # Böylece model hem sözdizimini (code) hem de ağaç mantığını (ast) aynı anda görecek.
        combined_text = code + " <AST_BASLANGICI> " + ast_string
        ssem_codes.append(combined_text)

    df['ssem_code'] = ssem_codes
    print(f"[BAŞARILI] {len(df)} adet kod, AST yapılarıyla birleştirildi (SSEM Aktif).")

    # 3. CODEBERT TOKENİZASYON AŞAMASI
    print("\n[ADIM 3] CodeBERT Tokenizasyon İşlemi (Vektörleştirme)...")
    # Koda AST yapısı da eklendiği için max_length değerini 128'den 256'ya çıkardık.
    tokenizer = CodeBertTokenizer(max_length=256)
    
    # Tokenizer'ı artık sadece 'code' değil, 'ssem_code' sütunu ile besliyoruz!
    vektorler = tokenizer.tokenize_dataset(df, code_column="ssem_code")

    # 4. İŞLENMİŞ VERİYİ KAYDETME AŞAMASI
    print("\n[ADIM 4] Eğitim İçin Hazırlanan Veri Kaydediliyor...")
    os.makedirs("data/processed", exist_ok=True)
    save_path = "data/processed/processed_dataset.pkl"

    df['input_ids'] = vektorler['input_ids'].tolist()
    df['attention_mask'] = vektorler['attention_mask'].tolist()

    df.to_pickle(save_path)
    
    print(f"\n✅ [BİTİŞ] Tüm boru hattı SSEM ve Dengeleme işlemleriyle başarıyla çalıştı!")
    print(f"📊 Yakıtımız, yapay zeka eğitimine hazır şekilde şuraya kaydedildi: {save_path}")

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    run_pipeline()