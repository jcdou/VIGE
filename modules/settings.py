import os
import json
import time
from colorama import Fore, Style, init
from urllib.parse import urlparse

init(autoreset=True)

# Mengimpor modul config secara keseluruhan untuk menghindari circular import
import modules.config as config_module

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
        print(f"1. WRAP_WIDTH: {config_module.CONFIG.get('WRAP_WIDTH', 'N/A')}")
        
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
                new_width_input = input(f"{Fore.WHITE}Masukkan lebar wrap teks baru (angka karakter, ketik 'batal' untuk membatalkan): {Style.RESET_ALL}").strip()
                if new_width_input.lower() == 'batal':
                    print(f"{Fore.YELLOW}Pembatalan pengeditan.{Style.RESET_ALL}")
                    time.sleep(0.5)
                    continue
                new_width = int(new_width_input)
                config_module.CONFIG['WRAP_WIDTH'] = new_width
                print(f"{Fore.GREEN}Lebar wrap teks diubah menjadi: {config_module.CONFIG['WRAP_WIDTH']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Lebar wrap harus berupa angka.{Style.RESET_ALL}")
        elif choice == '0':
            config_module.save_config(config_module.CONFIG)
            print(f"{Fore.GREEN}Pengaturan visual berhasil disimpan.{Style.RESET_ALL}")
            time.sleep(1)
            break
        else:
            print(f"{Fore.RED}Pilihan tidak valid. Silakan coba lagi.{Style.RESET_ALL}")
        
        input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")


def configure_settings():
    # Path untuk file konfigurasi dan cache tren
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_FILE_PATH = os.path.join(PROJECT_ROOT, 'config.json')
    OVERLAY_DIR = os.path.join(PROJECT_ROOT, 'overlay')
    TREND_CACHE_FILE_PATH = os.path.join(OVERLAY_DIR, os.path.basename(config_module.CONFIG.get('TREND_CACHE_FILE', 'trend_cache.json')))

    changes_made = False # Tambahkan flag untuk melacak perubahan

    while True:
        clear_screen()
        print(f"{Fore.CYAN}=== PENGATURAN KONFIGURASI ==={Style.RESET_ALL}")
        
        print(f"\n{Fore.BLUE}--- PATHS (Relatif dari root proyek) ---{Style.RESET_ALL}")
        print(f"1. MEDIA_DIR: {config_module.CONFIG.get('MEDIA_DIR', 'N/A')}")
        print(f"2. MUSIC_DIR: {config_module.CONFIG.get('MUSIC_DIR', 'N/A')}")
        print(f"3. FONT_DIR: {config_module.CONFIG.get('FONT_DIR', 'N/A')}")
        print(f"4. OUTPUT_DIR: {config_module.CONFIG.get('OUTPUT_DIR', 'N/A')}")
        print(f"5. OVERLAY_DIR: {config_module.CONFIG.get('OVERLAY_DIR', 'N/A')}")
        print(f"6. CAPTION_JSON: {config_module.CONFIG.get('CAPTION_JSON', 'N/A')}")
        print(f"7. CAPTION_TXT: {config_module.CONFIG.get('CAPTION_TXT', 'N/A')}")
        print(f"8. TREND_TXT: {config_module.CONFIG.get('TREND_TXT', 'N/A')}")

        print(f"\n{Fore.BLUE}--- API & TRENDS ---{Style.RESET_ALL}")
        print(f"9. AIML_API_KEY: {config_module.CONFIG.get('AIML_API_KEY', 'N/A')}")
        print(f"10. TREND_CACHE_DURATION: {config_module.CONFIG.get('TREND_CACHE_DURATION', 'N/A')} hours")
        print(f"11. TREND_CACHE_FILE: {config_module.CONFIG.get('TREND_CACHE_FILE', 'N/A')}")
        print(f"12. SOCIAL_PLATFORMS: {config_module.CONFIG.get('SOCIAL_PLATFORMS', 'N/A')}")
        print(f"13. MAX_API_CALLS_PER_HOUR: {config_module.CONFIG.get('MAX_API_CALLS_PER_HOUR', 'N/A')}")
        print(f"14. FALLBACK_PRIORITY: {config_module.CONFIG.get('FALLBACK_PRIORITY', 'N/A')}")
        print(f"15. TREND_LIMIT: {config_module.CONFIG.get('TREND_LIMIT', 'N/A')}")
        
        rss_feeds_display = [get_domain_from_url(url) for url in config_module.CONFIG.get('RSS_FEEDS', [])]
        print(f"16. RSS_FEEDS: {', '.join(rss_feeds_display) if rss_feeds_display else 'N/A'}")
        
        print(f"\n{Fore.RED}99. Reset ke Default{Style.RESET_ALL}") # Opsi reset baru
        print(f"{Fore.YELLOW}0. Kembali ke Menu Utama{Style.RESET_ALL}")
        
        choice = input(f"{Fore.CYAN}Pilih opsi untuk diubah (0-16, atau 99 untuk Reset): {Style.RESET_ALL}").strip()

        if choice == '0':
            if changes_made:
                print(f"{Fore.GREEN}Menyimpan perubahan konfigurasi...{Style.RESET_ALL}")
                config_module.save_config(config_module.CONFIG)
                print(f"{Fore.GREEN}Konfigurasi berhasil disimpan ke '{os.path.basename(CONFIG_FILE_PATH)}'.{Style.RESET_ALL}")
                # Muat ulang konfigurasi setelah disimpan untuk memastikan CONFIG global terbaru
                config_module.load_config()
            else:
                print(f"{Fore.BLUE}Tidak ada perubahan konfigurasi yang disimpan.{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Kembali ke menu utama.{Style.RESET_ALL}")
            time.sleep(1)
            break
        elif choice == '99': # Logika reset
            confirm_reset = input(f"{Fore.RED}PERINGATAN: Ini akan menghapus semua pengaturan kustom dan mengembalikannya ke default. Lanjutkan? (YA/TIDAK): {Style.RESET_ALL}").strip().upper()
            if confirm_reset == 'YA':
                if os.path.exists(CONFIG_FILE_PATH):
                    try:
                        os.remove(CONFIG_FILE_PATH)
                        print(f"{Fore.GREEN}✓ File konfigurasi '{os.path.basename(CONFIG_FILE_PATH)}' berhasil dihapus.{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}✗ Gagal menghapus file konfigurasi: {e}{Style.RESET_ALL}")
                        time.sleep(1)
                        continue # Kembali ke menu pengaturan
                
                # Muat ulang konfigurasi default
                config_module.load_config()
                print(f"{Fore.GREEN}✓ Konfigurasi berhasil direset ke default.{Style.RESET_ALL}")

                # Hapus cache tren juga
                if os.path.exists(TREND_CACHE_FILE_PATH):
                    try:
                        os.remove(TREND_CACHE_FILE_PATH)
                        print(f"{Fore.GREEN}✓ Cache tren ({os.path.basename(TREND_CACHE_FILE_PATH)}) berhasil dihapus untuk memaksa pengambilan tren baru.{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}✗ Gagal menghapus cache tren: {e}{Style.RESET_ALL}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"{Fore.YELLOW}Cache tren tidak ditemukan di {os.path.basename(TREND_CACHE_FILE_PATH)}. Tidak ada yang dihapus.{Style.RESET_ALL}")
                
                print(f"{Fore.BLUE}Pengaturan telah direset dan cache dibersihkan. Kembali ke menu utama.{Style.RESET_ALL}")
                time.sleep(2)
                break # Keluar dari menu pengaturan setelah reset
            else:
                print(f"{Fore.YELLOW}Reset dibatalkan.{Style.RESET_ALL}")
                time.sleep(0.5)
                continue # Kembali ke menu pengaturan

        try:
            choice_int = int(choice)
            if 1 <= choice_int <= 16:
                key_map = {
                    1: 'MEDIA_DIR', 2: 'MUSIC_DIR', 3: 'FONT_DIR', 4: 'OUTPUT_DIR',
                    5: 'OVERLAY_DIR', 6: 'CAPTION_JSON', 7: 'CAPTION_TXT', 8: 'TREND_TXT',
                    9: 'AIML_API_KEY', 10: 'TREND_CACHE_DURATION', 11: 'TREND_CACHE_FILE',
                    12: 'SOCIAL_PLATFORMS', 13: 'MAX_API_CALLS_PER_HOUR', 14: 'FALLBACK_PRIORITY',
                    15: 'TREND_LIMIT', 16: 'RSS_FEEDS'
                }
                selected_key = key_map[choice_int]
                current_value = config_module.CONFIG.get(selected_key)

                print(f"\n{Fore.YELLOW}Nilai saat ini untuk {selected_key}: {current_value}{Style.RESET_ALL}")
                new_value_input = input(f"{Fore.CYAN}Masukkan nilai baru untuk {selected_key} (ketik 'batal' untuk membatalkan): {Style.RESET_ALL}").strip()

                if new_value_input.lower() == 'batal':
                    print(f"{Fore.YELLOW}Pembatalan pengeditan.{Style.RESET_ALL}")
                    time.sleep(0.5)
                    continue # Kembali ke menu pengaturan tanpa mengubah nilai

                original_value = config_module.CONFIG.get(selected_key) # Simpan nilai asli
                
                if selected_key in ['TREND_CACHE_DURATION', 'MAX_API_CALLS_PER_HOUR', 'TREND_LIMIT']:
                    new_value = int(new_value_input)
                elif selected_key in ['SOCIAL_PLATFORMS', 'FALLBACK_PRIORITY', 'RSS_FEEDS']:
                    new_value = [item.strip() for item in new_value_input.split(',') if item.strip()]
                else:
                    new_value = new_value_input

                config_module.CONFIG[selected_key] = new_value
                
                # Hanya tandai perubahan jika nilai benar-benar berbeda
                if original_value != new_value:
                    changes_made = True
                    print(f"{Fore.GREEN}Nilai {selected_key} berhasil diubah menjadi: {new_value}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Nilai {selected_key} tidak berubah.{Style.RESET_ALL}")


            else:
                print(f"{Fore.RED}Pilihan tidak valid. Silakan masukkan angka antara 0-16, atau 99.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Masukan tidak valid. Harap masukkan angka yang benar atau format yang sesuai.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Terjadi kesalahan: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
        
        time.sleep(1) # Beri waktu pengguna untuk membaca pesan
