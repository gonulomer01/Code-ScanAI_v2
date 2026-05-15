using System;
using System.ComponentModel.DataAnnotations;

namespace CodeScanWeb.Models
{
    public class ScanResult
    {
        [Key]
        public int Id { get; set; }

        [Required]
        public string? CodeSnippet { get; set; } // Kullanıcının yapıştırdığı kod

        [Required]
        public string? Status { get; set; } // "Zafiyet Tespit Edildi" veya "Güvenli"

        [Required]
        public string? DetectedLanguage { get; set; } // C#, Python, C++

        public string? RepairSuggestion { get; set; } // Gemini'ın önerdiği düzeltilmiş kod

        public int ConfidenceScore { get; set; } // Güven oranı (%)

        public DateTime ScanDate { get; set; } = DateTime.Now; // Tarama tarihi
    }
}