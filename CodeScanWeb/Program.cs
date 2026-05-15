// 1. KÜTÜPHANELER EN ÜSTTE OLMALI
using Microsoft.EntityFrameworkCore;
using CodeScanWeb.Data; // Eğer senin projenin adı farklıysa, CodeScanWeb kısmını ona göre değiştir.

// 2. TEMEL ATILIYOR (builder değişkeni burada yaratılır)
var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();

// İŞTE EKSİK OLAN VE ÇÖKMEYİ DÜZELTECEK SATIR:
builder.Services.AddHttpClient();

// 3. VERİTABANI AYARI BURAYA GELECEK! (builder yaratıldıktan HEMEN SONRA)
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// 4. ÇATI KURULUYOR
var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseRouting();

app.UseAuthorization();

app.MapStaticAssets();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}")
    .WithStaticAssets();


app.Run();

