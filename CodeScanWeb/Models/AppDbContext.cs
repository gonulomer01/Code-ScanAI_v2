using Microsoft.EntityFrameworkCore;
using CodeScanWeb.Models;

namespace CodeScanWeb.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        public DbSet<ScanResult> ScanResults { get; set; }
    }
}