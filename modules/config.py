# modules/config.py
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

# ===== KONFIGURASI DEFAULT (Diperbarui tanpa pengaturan MoviePy) =====
DEFAULT_CONFIG = {
    # Font & Text (Hanya relevan untuk pembuatan caption, bukan rendering visual)
    'WRAP_WIDTH': 28, # Ini masih relevan untuk textwrap
    
    # Paths (relative to BASE_DIR, akan disesuaikan di load_config)
    'MEDIA_DIR': "assets/media", # Tetap ada, bisa untuk referensi atau fitur mendatang
    'MUSIC_DIR': "assets/music", # Tetap ada
    'FONT_DIR': "assets/font", # Tetap ada
    'OUTPUT_DIR': "output", # Untuk menyimpan hasil non-video
    'OVERLAY_DIR': "overlay",
    'CAPTION_JSON': "overlay/caption.json",
    'CAPTION_TXT': "overlay/caption.txt",
    'TREND_TXT': "overlay/trend.txt",
    'TREND_CACHE_DURATION': 24, # hours
    'TREND_CACHE_FILE': "trend_cache.json",
    'SOCIAL_PLATFORMS': ["tiktok", "youtube", "rss"],
    'MAX_API_CALLS_PER_HOUR': 60,
    'FALLBACK_PRIORITY': ["rss", "tiktok", "youtube"],
    'TREND_LIMIT': 5, # Number of trends to fetch/display
    'RSS_FEEDS': [ # Daftar RSS feeds yang akan digunakan
        "https://news.google.com/rss?hl=id&gl=ID&ceid=ID:id",
        "https://feeds.feedburner.com/beritaterkini",
        "https://rss.detik.com/index.php/tren"
    ],
    'YOUTUBE_API_KEY': "AIzaSyBqCldqAlXhHMJFkznDA5l6JRrcCKAjkDQ",  # ← isi dengann API YouTube
}

# Variabel global CONFIG yang akan diisi dengan pengaturan saat ini
CONFIG = {}

def get_config_path():
    """Mendapatkan path lengkap ke file konfigurasi."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'config.json')

def load_config():
    """
    Memuat konfigurasi dari config.json. Jika tidak ada atau error,
    akan menggunakan nilai DEFAULT_CONFIG.
    """
    global CONFIG
    config_path = get_config_path()
    
    temp_config = {}
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                temp_config.update(loaded)
            print(f"{Fore.GREEN}Konfigurasi dari 'config.json' berhasil dimuat.{Style.RESET_ALL}")
        except json.JSONDecodeError:
            print(f"{Fore.RED}Error: File 'config.json' rusak atau tidak valid. Menggunakan konfigurasi default.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error saat memuat 'config.json': {e}. Menggunakan konfigurasi default.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}File 'config.json' tidak ditemukan. Menggunakan konfigurasi default.{Style.RESET_ALL}")
    
    # Isi CONFIG dengan nilai default, lalu timpa dengan nilai yang dimuat jika tersedia
    for key, default_value in DEFAULT_CONFIG.items():
        if key in temp_config:
            CONFIG[key] = temp_config[key]
        else:
            if isinstance(default_value, (list, tuple, dict)):
                CONFIG[key] = default_value.__class__(default_value) 
            else:
                CONFIG[key] = default_value

    # Pastikan tipe data yang diharapkan tetap terjaga jika diubah dari list ke tuple atau sebaliknya di masa depan
    # Tidak ada lagi RESOLUTION atau FONT_OUTLINE yang perlu diubah ke tuple jika sudah dihapus dari config
    
    # Jika config.json tidak ada atau baru dibuat, simpan untuk mencerminkan default
    if not os.path.exists(config_path):
        save_config(CONFIG)


def save_config(current_config):
    """
    Menyimpan konfigurasi saat ini ke 'config.json'.
    """
    config_path = get_config_path()
    
    save_data = current_config.copy() 
    
    # Tidak ada lagi RESOLUTION atau FONT_OUTLINE yang perlu dikonversi kembali ke list
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=4, ensure_ascii=False) # ensure_ascii=False untuk karakter non-ASCII
        print(f"{Fore.GREEN}Konfigurasi berhasil disimpan ke '{os.path.basename(config_path)}'.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: Gagal menyimpan konfigurasi ke 'config.json': {e}{Style.RESET_ALL}")

# Karena load_config() dipanggil di start.py, kita tidak perlu memanggilnya di sini

# Panggil saat modul pertama kali diimpor
load_config()