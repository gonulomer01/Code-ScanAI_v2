import os
import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForSequenceClassification
from torch.optim import AdamW  # <-- İŞTE DEĞİŞİKLİK BURADA: Artık PyTorch'tan alıyoruz
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

class CodeDefectDataset(Dataset):
    """
    TÜBİTAK İP-2: PyTorch için özel veri seti sınıfı.
    Pickle dosyasındaki tensörleri modelin eğitim döngüsüne besler.
    """
    def __init__(self, df):
        self.input_ids = [torch.tensor(ids) for ids in df['input_ids'].tolist()]
        self.attention_masks = [torch.tensor(mask) for mask in df['attention_mask'].tolist()]
        self.labels = torch.tensor(df['label'].tolist(), dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            'input_ids': self.input_ids[idx],
            'attention_mask': self.attention_masks[idx],
            'labels': self.labels[idx]
        }

class ModelTrainer:
    def __init__(self, model_name="microsoft/codebert-base", num_labels=2):
        """
        CodeBERT modelini ve eğitim ayarlarını başlatır.
        """
        print(f"[SİSTEM] {model_name} modeli eğitim için yükleniyor...")
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"[BİLGİ] Eğitim için kullanılacak cihaz: {self.device}")

    def train_and_evaluate(self, data_path, epochs=3, batch_size=2):
        """
        Modeli eğitir ve başarımını değerlendirir.
        """
        print(f"\n[İŞLEM] Veri seti yükleniyor: {data_path}")
        df = pd.read_pickle(data_path)

        train_df, test_df = train_test_split(df, test_size=0.25, random_state=42)

        train_dataset = CodeDefectDataset(train_df)
        test_dataset = CodeDefectDataset(test_df)

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size)

        # Optimizasyon algoritması artık doğrudan PyTorch'tan çalışıyor
        optimizer = AdamW(self.model.parameters(), lr=2e-5)

        print("\n🚀 [EĞİTİM BAŞLIYOR]")
        for epoch in range(epochs):
            self.model.train()
            total_train_loss = 0

            for batch in train_loader:
                b_input_ids = batch['input_ids'].to(self.device)
                b_input_mask = batch['attention_mask'].to(self.device)
                b_labels = batch['labels'].to(self.device)

                self.model.zero_grad()

                outputs = self.model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask, labels=b_labels)
                loss = outputs.loss

                total_train_loss += loss.item()
                loss.backward()
                optimizer.step()

            avg_train_loss = total_train_loss / len(train_loader)
            print(f"  Epoch {epoch+1}/{epochs} | Ortalama Kayıp (Loss): {avg_train_loss:.4f}")

        print("\n📊 [TEST VE DEĞERLENDİRME]")
        self.model.eval()
        predictions, true_labels = [], []

        with torch.no_grad():
            for batch in test_loader:
                b_input_ids = batch['input_ids'].to(self.device)
                b_input_mask = batch['attention_mask'].to(self.device)
                b_labels = batch['labels'].to(self.device)

                outputs = self.model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
                logits = outputs.logits

                preds = torch.argmax(logits, dim=1).flatten()
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(b_labels.cpu().numpy())

        acc = accuracy_score(true_labels, predictions)
        f1 = f1_score(true_labels, predictions, zero_division=0)
        
        print(f"✅ Doğruluk (Accuracy): %{acc * 100:.2f}")
        print(f"✅ F1 Skoru: {f1:.4f}")

        save_dir = "models/fine_tuned_codebert"
        os.makedirs(save_dir, exist_ok=True)
        self.model.save_pretrained(save_dir)
        print(f"\n💾 [BAŞARILI] Eğitilmiş model kaydedildi: {save_dir}")

if __name__ == "__main__":
    trainer = ModelTrainer()
    veri_yolu = "data/processed/processed_dataset.pkl"
    
    if os.path.exists(veri_yolu):
        trainer.train_and_evaluate(veri_yolu, epochs=3)
    else:
        print(f"[HATA] İşlenmiş veri bulunamadı: {veri_yolu}")