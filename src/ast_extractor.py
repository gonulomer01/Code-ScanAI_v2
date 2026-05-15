from tree_sitter import Language, Parser
import tree_sitter_c_sharp as tscs
import tree_sitter_python as tspy
import tree_sitter_cpp as tscpp

class ASTExtractor:
    def __init__(self):
        """
        TÜBİTAK İP-1: Çoklu Dil Destekli Soyut Sözdizim Ağacı (AST) Çıkarıcı Modül.
        Gelen koda göre dinamik olarak C#, Python veya C++ derleyicisini seçer.
        """
        print("[SİSTEM] Çoklu Dil Ağaç Çıkarıcı (Router) başlatılıyor...")
        
        # Desteklenen dillerin sözlük (Dictionary) yapısında hafızaya alınması
        self.LANGUAGES = {
            "csharp": Language(tscs.language()),
            "python": Language(tspy.language()),
            "cpp": Language(tscpp.language())
        }
        self.parser = Parser()

    def detect_language(self, code):
        """
        Gelen kodun hangi dile ait olduğunu otomatik tespit eder.
        """
        # Python'a özgü anahtar kelimeler
        if "def " in code or ("import " in code and "public" not in code):
            return "python"
        # C++'a özgü anahtar kelimeler
        elif "#include" in code or "std::" in code or "cout" in code:
            return "cpp"
        # Varsayılan dil (TÜBİTAK ana hedefimiz)
        else:
            return "csharp"

    def extract_ast(self, source_code, forced_lang=None):
        """
        Verilen kodun ağaç yapısını oluşturur.
        Dili dinamik olarak belirler ve ilgili parser'ı (derleyiciyi) yükler.
        """
        # Eğer dil dışarıdan zorunlu verilmediyse otomatik tespit et
        detected_lang = forced_lang if forced_lang else self.detect_language(source_code)
        
        if detected_lang not in self.LANGUAGES:
            raise ValueError(f"[HATA] Desteklenmeyen dil: {detected_lang}")
            
        # Doğru dilin gramerini parser'a yükle (İşte dinamik yönlendirme burası)
        self.parser.language = self.LANGUAGES[detected_lang]
        
        tree = self.parser.parse(bytes(source_code, "utf8"))
        return tree.root_node, detected_lang

    def extract_node_types(self, node):
        """
        Ağaçtaki yapısal tipleri yapay zekanın (CodeBERT) anlayacağı liste formatında döndürür.
        """
        types = []
        if node.is_named:
            types.append(node.type)
        for child in node.children:
            types.extend(self.extract_node_types(child))
        return types

# --- TEST BLOĞU ---
if __name__ == "__main__":
    extractor = ASTExtractor()
    
    # 3 Farklı dilde yazılmış test kodları
    test_kodlari = [
        # 1. C# Kodu
        """
        public void Sil(string dosya) {
            File.Delete(dosya);
        }
        """,
        # 2. Python Kodu
        """
        def get_user(user_id):
            query = f"SELECT * FROM users WHERE id = {user_id}"
            db.execute(query)
        """,
        # 3. C++ Kodu
        """
        #include <iostream>
        using namespace std;
        int main() {
            int max_sum = 0;
            return max_sum;
        }
        """
    ]
    
    print("\n" + "="*50)
    for i, kod in enumerate(test_kodlari):
        # Sadece extract_ast diyoruz, o dili kendisi bulacak!
        root_node, tespit_edilen_dil = extractor.extract_ast(kod)
        yapisal_ozellikler = extractor.extract_node_types(root_node)
        
        print(f"🔸 {i+1}. KOD ANALİZİ")
        print(f"   - Otomatik Tespit Edilen Dil: {tespit_edilen_dil.upper()}")
        print(f"   - Çıkarılan AST (İlk 5 Düğüm): {yapisal_ozellikler[:5]}")
        print("-" * 50)