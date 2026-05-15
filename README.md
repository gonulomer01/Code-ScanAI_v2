# 🛡️ CodeScanAI v2.0 - Hybrid AI Security Scanner

CodeScanAI, yazılım geliştirme süreçlerinde kaynak kod zafiyetlerini (vulnerability) tespit etmek ve onarmak için geliştirilmiş, **SSEM (Semantic-Syntactic Embedding Model)** mimarisine ve **Geri Bildirim Döngüsüne (Feedback Loop)** sahip profesyonel bir siber güvenlik aracıdır.

Proje, geleneksel statik kod analizi (SAST) araçlarının ötesine geçerek; kodu sadece metin olarak değil, **AST (Abstract Syntax Tree)** düğümleri üzerinden yapısal olarak anlar. Tespit edilen zafiyetler için yapay zeka destekli, derleyici onaylı güvenli onarım yamaları (patches) üretir.

## 🚀 Öne Çıkan Mühendislik Çözümleri

* **Hibrit Analiz Motoru (CodeBERT + AST):** Sadece koda değil, dilin yapısal ağacına da (AST) odaklanarak farklı programlama dillerindeki (C#, Python, C++) benzer mantıksal zafiyetleri aynı vektör uzayında yakalar.
* **Heuristic False-Positive Filtresi:** Yapay zekanın "Asılsız Alarm" (False Positive) üretme ihtimaline karşı, araya girerek kodun içindeki güvenlik önlemlerini (örneğin `Path.GetFileName`, sanitization metodları) denetleyen özel bir algoritmaya sahiptir.
* **AI Feedback Loop (Oto-Onarım):** Zafiyet bulunduğunda Gemini AI modeli ile güvenli kod üretilir. Üretilen kod, izole bir ortamda derleyici (compiler) testinden geçirilir. Hata alırsak, hata logu yapay zekaya geri beslenir ve yama kusursuz hale gelene kadar döngü devam eder.
* **Side-by-Side Diff View:** ASP.NET Core tabanlı modern ön yüz (frontend), mühendislerin hatalı kod ile yapay zekanın onardığı kodu yan yana (Prism.js syntax highlighting ile) karşılaştırmasına olanak tanır.

## 🧠 Mimari Şema

Sistem, iki bağımsız sunucunun (Microservice mimarisi) asenkron iletişimine dayanır:

1. **Backend (Yapay Zeka & Analiz - FastAPI):** CodeBERT modelini, AST çıkarıcıları ve LLM entegrasyonunu barındıran çekirdek Python sunucusu.
2. **Frontend (Kullanıcı Arayüzü - ASP.NET Core MVC):** Geliştiricilerin kodlarını yüklediği, analiz süreçlerini anlık (loading states) takip ettiği, C# tabanlı güvenli web arayüzü.

## 🛠️ Kullanılan Teknolojiler

* **Yapay Zeka:** Hugging Face `transformers` (CodeBERT), PyTorch, Google Gemini Pro.
* **Backend API:** Python, FastAPI, Uvicorn, AST (Abstract Syntax Tree).
* **Frontend & Sunucu:** C#, .NET Core MVC, Bootstrap 5, Prism.js, JavaScript, AJAX.

## ⚙️ Kurulum ve Çalıştırma

Proje, yapay zeka ağırlık dosyalarının (500+ MB) boyutundan dolayı GitHub'da sadece kaynak kod olarak yer almaktadır. Sistemi yerelde (localhost) tam kapasite çalıştırmak için aşağıdaki adımları izleyin:

### 1. Yapay Zeka Ağırlıklarının Eklenmesi
* `fine_tuned_codebert` klasörü içerisine, sistemin eğitilmiş ağırlıkları olan `model.safetensors` ve `config.json` dosyalarını dahil edin.

### 2. Python (AI) Sunucusunu Başlatma
Projenin ana dizininde bir terminal açın, sanal ortamı (`venv`) aktif edin ve FastAPI sunucusunu ayağa kaldırın:

```bash
venv\Scripts\activate
uvicorn src.api_service:app --reload
```

Terminalde %87.54'lük Beyin uyandırıldı mesajını görmelisiniz.

### 3. Web Arayüzünü Başlatma
Yeni bir terminal açın ve .NET Core MVC projesini başlatın:

```bash
cd CodeScanWeb
dotnet run
```

Tarayıcınızda terminalin size verdiği adrese (örneğin http://localhost:5xxx) giderek arayüze erişebilirsiniz.

Projeyi çalıştırmak için https://drive.google.com/file/d/1Dxqd3t5ejJRjxMTfuN7_uvJRTszFNnWq/view?usp=sharing linkinden indireceğiniz model.safetensors dosyasını src/fine_tuned_codebert klasörüne eklemeniz gerekir. Ayrıca src/api_service.py dosyasının 29. satırına google ai studio ile ücretsiz alabileceğiniz gemini api key'ini girmeniz gerekir.

Bu proje, yapay zeka ile modern web teknolojilerinin siber güvenlik alanında nasıl bütünleşik ve kurumsal ölçekte kullanılabileceğini göstermek amacıyla geliştirilmiştir.
