# modules/settings.py
import os
import sys
import time
from colorama import Fore, Style, init
from urllib.parse import urlparse

init(autoreset=True)

from modules.config import CONFIG, save_config

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_domain_from_url(url):
    """Mengekstrak nama domain dari URL."""
    try:
        return urlparse(url).netloc.replace('www.', '')
    except Exception:
        return url # Kembali ke URL asli jika gagal

def configure_visual_options():
    """
    Menampilkan dan mengkonfigurasi opsi visual aplikasi.
    """
    while True:
        clear_screen()
        print(f"{Fore.CYAN}=== OPSI VISUAL ==={Style.RESET_ALL}")
        print(f"{Fore.GREEN}--- PENGATURAN TEKS & CAPTION ---{Style.RESET_ALL}")
        print(f"1. WRAP_WIDTH: {CONFIG.get('WRAP_WIDTH', 'N/A')}")
        
        print(f"\n{Fore.GREEN}--- PENGATURAN VIDEO (Placeholder) ---{Style.RESET_ALL}")
        print(f"2. Pilih Font (saat ini acak)")
        print(f"3. Warna Caption (Placeholder)")
        print(f"4. Animasi Fading Teks (Placeholder)")
        print(f"5. Pengaturan Audio Fading (Placeholder)")
        print(f"6. Pengaturan FFmpeg Lanjutan (Placeholder)")

        print(f"\n{Fore.YELLOW}0. Kembali ke Menu Utama{Style.RESET_ALL}") # Kembali ke main_menu_app

        choice = input(f"{Fore.CYAN}Pilih opsi untuk diubah (0-6): {Style.RESET_ALL}").strip()

        if choice == '1': # WRAP_WIDTH
            try:
                new_width = int(input(f"{Fore.WHITE}Masukkan lebar wrap teks baru (angka karakter): {Style.RESET_ALL}"))
                CONFIG['WRAP_WIDTH'] = new_width
                print(f"{Fore.GREEN}Lebar wrap teks diubah menjadi: {CONFIG['WRAP_WIDTH']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Lebar wrap harus berupa angka.{Style.RESET_ALL}")
        elif choice == '0':
            save_config(CONFIG)
            print(f"{Fore.BLUE}Pengaturan visual disimpan dan kembali.{Style.RESET_ALL}")
            time.sleep(1)
            break
        else:
            print(f"{Fore.RED}Pilihan tidak valid. Silakan coba lagi.{Style.RESET_ALL}")
        
        save_config(CONFIG)
        input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")


def configure_settings():
    while True:
        clear_screen()
        print(f"{Fore.CYAN}=== PENGATURAN KONFIGURASI ==={Style.RESET_ALL}")
        
        # Opsi Visual telah dipindahkan ke menu utama, jadi dihapus dari sini
        # print(f"{Fore.GREEN}--- OPSI VISUAL ---{Style.RESET_ALL}")
        # print(f"1. Pengaturan Visual (Teks, Font, Warna, Animasi, dll.)")

        print(f"\n{Fore.GREEN}--- PATHS (Relatif dari root proyek) ---{Style.RESET_ALL}")
        print(f"1. MEDIA_DIR: {CONFIG.get('MEDIA_DIR', 'N/A')}") # Nomor disesuaikan
        print(f"2. MUSIC_DIR: {CONFIG.get('MUSIC_DIR', 'N/A')}")
        print(f"3. FONT_DIR: {CONFIG.get('FONT_DIR', 'N/A')}")
        print(f"4. OUTPUT_DIR: {CONFIG.get('OUTPUT_DIR', 'N/A')}")
        print(f"5. OVERLAY_DIR: {CONFIG.get('OVERLAY_DIR', 'N/A')}")
        print(f"6. CAPTION_JSON: {CONFIG.get('CAPTION_JSON', 'N/A')}")
        print(f"7. CAPTION_TXT: {CONFIG.get('CAPTION_TXT', 'N/A')}")
        print(f"8. TREND_TXT: {CONFIG.get('TREND_TXT', 'N/A')}")

        print(f"\n{Fore.GREEN}--- API & TRENDS ---{Style.RESET_ALL}")
        print(f"9. AIML_API_KEY: {CONFIG.get('AIML_API_KEY', 'N/A')}")
        print(f"10. TREND_CACHE_DURATION: {CONFIG.get('TREND_CACHE_DURATION', 'N/A')} hours")
        print(f"11. TREND_CACHE_FILE: {CONFIG.get('TREND_CACHE_FILE', 'N/A')}")
        print(f"12. SOCIAL_PLATFORMS: {CONFIG.get('SOCIAL_PLATFORMS', 'N/A')}")
        print(f"13. MAX_API_CALLS_PER_HOUR: {CONFIG.get('MAX_API_CALLS_PER_HOUR', 'N/A')}")
        print(f"14. FALLBACK_PRIORITY: {CONFIG.get('FALLBACK_PRIORITY', 'N/A')}")
        print(f"15. TREND_LIMIT: {CONFIG.get('TREND_LIMIT', 'N/A')}")
        
        rss_feeds_display = [get_domain_from_url(url) for url in CONFIG.get('RSS_FEEDS', [])]
        print(f"16. RSS_FEEDS: {', '.join(rss_feeds_display) if rss_feeds_display else 'N/A'}") # Nomor disesuaikan
        
        print(f"\n{Fore.YELLOW}0. Kembali ke Menu Utama{Style.RESET_ALL}")
        
        choice = input(f"{Fore.CYAN}Pilih opsi untuk diubah (0-16): {Style.RESET_ALL}").strip() # Rentang pilihan disesuaikan

        if choice == '1': # MEDIA_DIR (sebelumnya 2)
            new_dir = input(f"{Fore.WHITE}Masukkan folder media baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['MEDIA_DIR'] = new_dir
            print(f"{Fore.GREEN}Folder media diubah menjadi: {CONFIG['MEDIA_DIR']}{Style.RESET_ALL}")
        elif choice == '2': # MUSIC_DIR (sebelumnya 3)
            new_dir = input(f"{Fore.WHITE}Masukkan folder musik baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['MUSIC_DIR'] = new_dir
            print(f"{Fore.GREEN}Folder musik diubah menjadi: {CONFIG['MUSIC_DIR']}{Style.RESET_ALL}")
        elif choice == '3': # FONT_DIR (sebelumnya 4)
            new_dir = input(f"{Fore.WHITE}Masukkan folder font baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['FONT_DIR'] = new_dir
            print(f"{Fore.GREEN}Folder font diubah menjadi: {CONFIG['FONT_DIR']}{Style.RESET_ALL}")
        elif choice == '4': # OUTPUT_DIR (sebelumnya 5)
            new_dir = input(f"{Fore.WHITE}Masukkan folder output baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['OUTPUT_DIR'] = new_dir
            print(f"{Fore.GREEN}Folder output diubah menjadi: {CONFIG['OUTPUT_DIR']}{Style.RESET_ALL}")
        elif choice == '5': # OVERLAY_DIR (sebelumnya 6)
            new_dir = input(f"{Fore.WHITE}Masukkan folder overlay baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['OVERLAY_DIR'] = new_dir
            print(f"{Fore.GREEN}Folder overlay diubah menjadi: {CONFIG['OVERLAY_DIR']}{Style.RESET_ALL}")
        elif choice == '6': # CAPTION_JSON (sebelumnya 7)
            new_path = input(f"{Fore.WHITE}Masukkan path CAPTION_JSON baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['CAPTION_JSON'] = new_path
            print(f"{Fore.GREEN}CAPTION_JSON diubah menjadi: {CONFIG['CAPTION_JSON']}{Style.RESET_ALL}")
        elif choice == '7': # CAPTION_TXT (sebelumnya 8)
            new_path = input(f"{Fore.WHITE}Masukkan path CAPTION_TXT baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['CAPTION_TXT'] = new_path
            print(f"{Fore.GREEN}CAPTION_TXT diubah menjadi: {CONFIG['CAPTION_TXT']}{Style.RESET_ALL}")
        elif choice == '8': # TREND_TXT (sebelumnya 9)
            new_path = input(f"{Fore.WHITE}Masukkan path TREND_TXT baru (path relatif/absolut): {Style.RESET_ALL}").strip()
            CONFIG['TREND_TXT'] = new_path
            print(f"{Fore.GREEN}TREND_TXT diubah menjadi: {CONFIG['TREND_TXT']}{Style.RESET_ALL}")
        elif choice == '9': # AIML_API_KEY (sebelumnya 10)
            new_key = input(f"{Fore.WHITE}Masukkan AIML_API_KEY baru: {Style.RESET_ALL}").strip()
            CONFIG['AIML_API_KEY'] = new_key
            print(f"{Fore.GREEN}AIML_API_KEY diubah menjadi: {CONFIG['AIML_API_KEY']}{Style.RESET_ALL}")
        elif choice == '10': # TREND_CACHE_DURATION (sebelumnya 11)
            try:
                new_duration = int(input(f"{Fore.WHITE}Masukkan durasi cache tren baru (jam): {Style.RESET_ALL}"))
                CONFIG['TREND_CACHE_DURATION'] = new_duration
                print(f"{Fore.GREEN}Durasi cache tren diubah menjadi: {CONFIG['TREND_CACHE_DURATION']} jam{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Durasi harus berupa angka.{Style.RESET_ALL}")
        elif choice == '11': # TREND_CACHE_FILE (sebelumnya 12)
            new_file = input(f"{Fore.WHITE}Masukkan nama file cache tren baru: {Style.RESET_ALL}").strip()
            CONFIG['TREND_CACHE_FILE'] = new_file
            print(f"{Fore.GREEN}Nama file cache tren diubah menjadi: {CONFIG['TREND_CACHE_FILE']}{Style.RESET_ALL}")
        elif choice == '12': # SOCIAL_PLATFORMS (sebelumnya 13)
            new_platforms_str = input(f"{Fore.WHITE}Masukkan platform sosial baru (pisahkan dengan koma, misal: tiktok,youtube,rss): {Style.RESET_ALL}").strip()
            CONFIG['SOCIAL_PLATFORMS'] = [p.strip() for p in new_platforms_str.split(',') if p.strip()]
            print(f"{Fore.GREEN}Platform sosial diubah menjadi: {CONFIG['SOCIAL_PLATFORMS']}{Style.RESET_ALL}")
        elif choice == '13': # MAX_API_CALLS_PER_HOUR (sebelumnya 14)
            try:
                new_limit = int(input(f"{Fore.WHITE}Masukkan batas panggilan API per jam baru: {Style.RESET_ALL}"))
                CONFIG['MAX_API_CALLS_PER_HOUR'] = new_limit
                print(f"{Fore.GREEN}Batas panggilan API diubah menjadi: {CONFIG['MAX_API_CALLS_PER_HOUR']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Batas panggilan API harus berupa angka.{Style.RESET_ALL}")
        elif choice == '14': # FALLBACK_PRIORITY (sebelumnya 15)
            new_priority_str = input(f"{Fore.WHITE}Masukkan prioritas fallback baru (pisahkan dengan koma, misal: rss,tiktok,youtube): {Style.RESET_ALL}").strip()
            CONFIG['FALLBACK_PRIORITY'] = [p.strip() for p in new_priority_str.split(',') if p.strip()]
            print(f"{Fore.GREEN}Prioritas fallback diubah menjadi: {CONFIG['FALLBACK_PRIORITY']}{Style.RESET_ALL}")
        elif choice == '15': # TREND_LIMIT (sebelumnya 16)
            try:
                new_limit = int(input(f"{Fore.WHITE}Masukkan batas tren yang akan diambil: {Style.RESET_ALL}"))
                CONFIG['TREND_LIMIT'] = new_limit
                print(f"{Fore.GREEN}Batas tren diubah menjadi: {CONFIG['TREND_LIMIT']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Batas tren harus berupa angka.{Style.RESET_ALL}")
        elif choice == '16': # RSS_FEEDS (sebelumnya 17)
            print(f"{Fore.BLUE}RSS Feeds saat ini: {CONFIG['RSS_FEEDS']}{Style.RESET_ALL}")
            new_rss_feeds_str = input(f"{Fore.WHITE}Masukkan RSS feeds baru (pisahkan dengan koma, URL lengkap): {Style.RESET_ALL}").strip()
            CONFIG['RSS_FEEDS'] = [url.strip() for url in new_rss_feeds_str.split(',') if url.strip()]
            print(f"{Fore.GREEN}RSS Feeds diubah menjadi: {CONFIG['RSS_FEEDS']}{Style.RESET_ALL}")
        elif choice == '0':
            save_config(CONFIG)
            print(f"{Fore.BLUE}Pengaturan disimpan dan kembali ke menu utama.{Style.RESET_ALL}")
            time.sleep(1)
            break
        else:
            print(f"{Fore.RED}Pilihan tidak valid. Silakan coba lagi.{Style.RESET_ALL}")
        
        save_config(CONFIG)
        input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")
