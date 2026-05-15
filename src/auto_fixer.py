import ollama

class AutoFixer:
    def __init__(self, model_name="llama3"):
        """
        TÜBİTAK İP-3: Üretken Yapay Zeka (LLM) Onarım Modülü.
        Ollama üzerinden yerel (offline) çalışan Llama-3 modelini kullanır.
        """
        self.model_name = model_name
        print(f"[SİSTEM] {self.model_name} (Ollama) Onarım Motoru başlatılıyor...")

    def fix_code(self, broken_code, vulnerability_type="Güvenlik Zafiyeti"):
        """
        Hatalı kodu alır, bağlamı anlar ve düzeltilmiş güvenli versiyonunu üretir.
        """
        print(f"\n[İŞLEM] Yapay Zeka '{vulnerability_type}' zafiyetini inceliyor...")
        print("[BİLGİ] Çözüm (Yama) üretiliyor, lütfen bekleyin...")

        # Prompt Engineering: Modele bir "Rol" ve kesin "Kurallar" veriyoruz
        prompt = f"""
        Sen kıdemli bir Siber Güvenlik Uzmanı ve Yazılım Mühendisisin.
        Aşağıdaki kodda bir '{vulnerability_type}' tespit edildi.
        
        Görevlerin:
        1. Bu kodu %100 güvenli hale getirecek şekilde yeniden yaz.
        2. Kodu yazarken SADECE düzeltilmiş kodu ver, ekstra açıklama, merhaba vs. yazma.
        3. Kodun doğrudan derlenebilir (çalışır) olduğundan emin ol.

        Hatalı Kod:
        {broken_code}
        """

        try:
            # İnternetsiz, tamamen lokalde çalışan Llama-3 ile iletişim
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            return response['message']['content']
            
        except Exception as e:
            return f"[HATA] Ollama ile iletişim kurulamadı: {e}\nLütfen Ollama'nın açık olduğundan emin olun."

# --- TEST BLOĞU ---
if __name__ == "__main__":
    fixer = AutoFixer()
    
    # Klasik ve çok tehlikeli bir SQL Injection örneği
    hatali_csharp_kodu = """
    public User GetUser(string username) {
        string query = "SELECT * FROM Users WHERE Username = '" + username + "'";
        SqlCommand cmd = new SqlCommand(query, connection);
        return cmd.ExecuteReader();
    }
    """
    
    print("-" * 50)
    print("❌ HATALI KOD GELİYOR:")
    print(hatali_csharp_kodu.strip())
    print("-" * 50)
    
    # Motoru çalıştır
    guvenli_kod = fixer.fix_code(hatali_csharp_kodu, "SQL Injection")
    
    print("\n" + "=" * 50)
    print("✅ GÜVENLİ KOD (LLAMA-3 YAMASI):")
    print(guvenli_kod)
    print("=" * 50)