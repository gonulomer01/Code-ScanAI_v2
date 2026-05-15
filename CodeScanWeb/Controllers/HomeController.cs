using Microsoft.AspNetCore.Mvc;
using CodeScanWeb.Data;
using CodeScanWeb.Models;
using System.Text.Json;
using System.Text;
using Microsoft.EntityFrameworkCore;

namespace CodeScanWeb.Controllers
{
    public class HomeController : Controller
    {
        private readonly AppDbContext _context;
        private readonly HttpClient _httpClient;

        public HomeController(AppDbContext context, IHttpClientFactory httpClientFactory)
        {
            _context = context;
            _httpClient = httpClientFactory.CreateClient();
        }

        public IActionResult Index()
        {
            return View();
        }

        public IActionResult Privacy()
        {
            return View();
        }

        public async Task<IActionResult> History()
        {
            // Veritabanındaki tüm tarama sonuçlarını en yeni en üstte olacak şekilde getirir
            var history = await _context.ScanResults
                                .OrderByDescending(s => s.ScanDate)
                                .ToListAsync();
            return View(history);
        }

        [HttpPost]
        public async Task<IActionResult> ScanCode([FromBody] ScanRequest request)
        {
            if (string.IsNullOrEmpty(request.Code))
            {
                return BadRequest("Lütfen analiz edilecek bir kod yapıştırın.");
            }

            try
            {
                // Python API'ye istek gönderme
                var payload = new
                {
                    code = request.Code,
                    language = request.Language
                };

                var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync("http://127.0.0.1:8000/analyze", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseString = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<ScanApiResponse>(responseString);

                    // SARI UYARIYI GİDERECEK GÜVENLİK KONTROLÜ:
                    if (result == null) 
                    {
                        return StatusCode(500, "Yapay zeka servisinden boş veya geçersiz bir yanıt döndü.");
                    }

                    // --- TÜBİTAK İP-4 VAADİ: MSSQL VERİTABANINA ASENKRON KAYIT ---
                    // --- DOĞRU KAYIT BLOĞU ---
                    var dbRecord = new ScanResult
                    {
                        CodeSnippet = request.Code, // <--- BURASI ÇOK KRİTİK! Kullanıcının yazdığı orijinal kod buraya atanmalı.
                        Status = result.status,
                        DetectedLanguage = result.detected_language,
                        RepairSuggestion = result.repair_suggestion,
                        ConfidenceScore = int.Parse(result.confidence?.Replace("%", "") ?? "0"),
                        ScanDate = DateTime.Now
                    };

                    _context.ScanResults.Add(dbRecord);
                    await _context.SaveChangesAsync();

                    return Json(result);
                }

                return StatusCode(500, "Python API bağlantı hatası oluştu.");
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Sistem hatası: {ex.Message}");
            }
        }
        
        [HttpPost]
        public async Task<IActionResult> DeleteRecord(int id)
        {
            var record = await _context.ScanResults.FindAsync(id);
            if (record == null)
            {
                return NotFound();
            }

            _context.ScanResults.Remove(record);
            await _context.SaveChangesAsync();

            return Ok(); // Başarılıysa 200 döner
        }
    }

    // İstek ve Yanıt DTO Modelleri
    public class ScanRequest
    {
        public string? Code { get; set; }
        public string? Language { get; set; }
    }

    public class ScanApiResponse
    {
        public string? status { get; set; }
        public string? confidence { get; set; }
        public string? detected_language { get; set; }
        public string? repair_suggestion { get; set; }
    }
}