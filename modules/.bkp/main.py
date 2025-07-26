import os
import sys
import time
import json
import subprocess
import shutil # Import shutil for terminal size
import random # Import random for batch generation

from colorama import Fore, Style, init

init(autoreset=True)

# BASE_DIR harus diatur di sini agar relatif terhadap lokasi main.py
# Ketika main.py diimpor, __file__ adalah path ke main.py itu sendiri.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR) # Tambahkan modules/ ke sys.path jika belum ada

from modules.config import CONFIG, load_config
from modules.settings import configure_settings, configure_visual_options
from modules.trend_scraper import update as update_trends # Alias 'update' dari TrendScraper
from modules.video_renderer import VideoRenderer

# Impor display_captions dari styled_caption_generator jika ingin menggunakannya
from modules.styled_caption_generator import display_captions as display_styled_captions

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading(message="Loading...", delay=1.0):
    # Fungsi loading ini bisa dipertahankan untuk pesan umum,
    # tetapi tidak digunakan untuk progres render video.
    print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")
    time.sleep(delay)

def list_module_files():
    clear_screen()
    required_files = [
        "__init__.py", "main.py", "config.py", "license.py",
        "trend_scraper.py", "styled_caption_generator.py",
        "settings.py", "scraper.py", "video_renderer.py"
    ]

    modules_dir_path = BASE_DIR  

    existing_files = []  
    if os.path.exists(modules_dir_path):  
        existing_files = os.listdir(modules_dir_path)  
      
    print(f"\n{Fore.CYAN}=== STATUS FILE MODUL ==={Style.RESET_ALL}")  
    print(f"{Fore.YELLOW}Folder modules/:{Style.RESET_ALL}")  
      
    print(f"\n{Fore.GREEN}File yang sudah ada (diperlukan):{Style.RESET_ALL}")  
    found_any_required = False  
    for file in required_files:  
        if file in existing_files:  
            print(f"  ✓ {file}")  
            found_any_required = True  
    if not found_any_required:  
        print(f"  {Fore.RED}Tidak ada file modul yang diperlukan ditemukan{Style.RESET_ALL}")  
      
    print(f"\n{Fore.RED}File yang belum ada (diperlukan):{Style.RESET_ALL}")  
    missing_any = False  
    for file in required_files:  
        if file not in existing_files:  
            print(f"  ✗ {file}")  
            missing_any = True  
    if not missing_any:  
        print(f"  {Fore.GREEN}Semua file modul yang diperlukan tersedia{Style.RESET_ALL}")  
      
    additional_files = [f for f in existing_files if f not in required_files and f.endswith('.py')]  
    if additional_files:  
        print(f"\n{Fore.BLUE}File Python tambahan lainnya:{Style.RESET_ALL}")  
        for file in additional_files:  
            print(f"  • {file}")  
    else:  
        print(f"\n{Fore.BLUE}Tidak ada file Python tambahan di folder modules/.{Style.RESET_ALL}")

def check_dependencies():
    required_files = [
        "__init__.py", "main.py", "config.py", "license.py",
        "trend_scraper.py", "styled_caption_generator.py",
        "settings.py", "scraper.py", "video_renderer.py"
    ]

    missing_files = []  
    for file_name in required_files:  
        if not os.path.exists(os.path.join(BASE_DIR, file_name)):  
            missing_files.append(file_name)  
      
    if missing_files:  
        print(f"{Fore.RED}Error: File penting berikut tidak ditemukan:{Style.RESET_ALL}")  
        for file in missing_files:  
            print(f"  - modules/{file}")  
        return False  
      
    list_module_files()  
      
    return True

def create_directories():
    project_root = os.path.dirname(BASE_DIR)

    directories = [  
        os.path.join(project_root, "overlay"),  
        os.path.join(project_root, "assets", "media"),  
        os.path.join(project_root, "assets", "music"),  
        os.path.join(project_root, "output"),  
        os.path.join(project_root, "assets", "font")  
    ]  
      
    for full_path in directories:  
        relative_path = os.path.relpath(full_path, project_root)  
        if not os.path.exists(full_path):  
            os.makedirs(full_path)  
            print(f"{Fore.GREEN}✓ Created directory: {relative_path}{Style.RESET_ALL}")  
    else:  
        pass # Mengabaikan pesan jika direktori sudah ada

def validate_environment():
    if sys.version_info < (3, 7):
        print(f"{Fore.RED}Error: Python 3.7 atau lebih tinggi diperlukan. Versi Anda: {sys.version.split(' ')[0]}{Style.RESET_ALL}")
        return False

    try:  
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)  
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True, text=True)  
        print(f"{Fore.GREEN}✓ FFmpeg dan FFprobe ditemukan.{Style.RESET_ALL}")  
        return True  
    except (subprocess.CalledProcessError, FileNotFoundError):  
        print(f"{Fore.RED}Error: FFmpeg atau FFprobe tidak ditemukan. Fitur rendering video tidak akan berfungsi.{Style.RESET_ALL}")  
        return False

def check_required_assets():
    clear_screen()
    print(f"{Fore.CYAN}=== PEMERIKSAAN ASET ==={Style.RESET_ALL}")
    project_root = os.path.dirname(BASE_DIR)
    
    missing_assets_info = []

    # Periksa file video di assets/media
    media_dir_path = os.path.join(project_root, CONFIG.get('MEDIA_DIR', 'assets/media'))
    if not os.path.exists(media_dir_path):
        missing_assets_info.append(("Assets Media", f"Direktori '{os.path.relpath(media_dir_path, project_root)}' tidak ditemukan."))
    else:
        video_files = [f for f in os.listdir(media_dir_path) if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
        if not video_files:
            missing_assets_info.append(("Assets Media", f"Tidak ada file video di '{os.path.relpath(media_dir_path, project_root)}'."))

    # Periksa file musik di assets/music
    music_dir_path = os.path.join(project_root, CONFIG.get('MUSIC_DIR', 'assets/music'))
    if not os.path.exists(music_dir_path):
        missing_assets_info.append(("Assets Audio", f"Direktori '{os.path.relpath(music_dir_path, project_root)}' tidak ditemukan."))
    else:
        audio_files = [f for f in os.listdir(music_dir_path) if f.lower().endswith((".mp3", ".wav", ".aac"))]
        if not audio_files:
            missing_assets_info.append(("Assets Audio", f"Tidak ada file audio di '{os.path.relpath(music_dir_path, project_root)}'."))

    # Periksa file caption di overlay/
    # Pastikan path overlay selalu dimulai dari project_root dan 'overlay'
    overlay_base_path = os.path.join(project_root, 'overlay')
    
    # Gunakan os.path.basename untuk memastikan kita hanya mendapatkan nama file dari CONFIG
    caption_json_filename = os.path.basename(CONFIG.get('CAPTION_JSON', 'caption.json'))
    caption_txt_filename = os.path.basename(CONFIG.get('CAPTION_TXT', 'caption.txt'))

    caption_json_path = os.path.join(overlay_base_path, caption_json_filename)
    caption_txt_path = os.path.join(overlay_base_path, caption_txt_filename)

    caption_found = False
    if not os.path.exists(overlay_base_path): # Check if the base overlay directory exists
        missing_assets_info.append(("Overlay Caption", f"Direktori '{os.path.relpath(overlay_base_path, project_root)}' tidak ditemukan."))
    else:
        if os.path.exists(caption_json_path):
            try:
                with open(caption_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if any(item.get('text') for item in data): # Cek apakah ada caption valid
                        caption_found = True
            except (json.JSONDecodeError, KeyError):
                pass # Lanjut cek TXT jika JSON error
        
        if not caption_found and os.path.exists(caption_txt_path):
            with open(caption_txt_path, 'r', encoding='utf-8') as f:
                if any(line.strip() for line in f): # Cek apakah ada baris tidak kosong
                    caption_found = True
    
    if not caption_found:
        missing_assets_info.append(("Overlay Caption", f"Tidak ada file caption valid ({caption_json_filename} atau {caption_txt_filename}) di '{os.path.relpath(overlay_base_path, project_root)}'."))

    if missing_assets_info:
        print(f"\n{Fore.YELLOW}⚠️ Is Missing:{Style.RESET_ALL}")
        missing_elements = []
        for asset_type, problem_info in missing_assets_info:
            print(f"- {asset_type} {Fore.RED}[X]{Style.RESET_ALL}")
            print(f"  ({problem_info})")
            # Tambahkan nama elemen yang hilang untuk pesan peringatan
            if "Media" in asset_type:
                missing_elements.append("video")
            elif "Audio" in asset_type:
                missing_elements.append("audio")
            elif "Caption" in asset_type:
                missing_elements.append("caption")
        
        missing_elements_str = ", ".join(missing_elements) if missing_elements else "tertentu"
        print(f"\n{Fore.YELLOW}Melanjutkan tanpa aset ini akan rendering video tanpa elemen {missing_elements_str}.{Style.RESET_ALL}")
        print(f"Apakah Anda ingin melanjutkan proses pembuatan video?")
        print(f"1. Lanjutkan")
        print(f"0. Kembali ke Menu Utama")
        
        choice = input(f"{Fore.CYAN}Pilih opsi (1/0): {Style.RESET_ALL}").strip()
        return choice == '1'
    else:
        print(f"\n{Fore.GREEN}✓ Semua aset yang diperlukan ditemukan. Melanjutkan...{Style.RESET_ALL}")
        time.sleep(1) # Beri waktu pengguna untuk membaca pesan
        return True

def generate_video_process():
    clear_screen()
    print(f"{Fore.CYAN}=== GENERATE VIDEO KUSTOM ==={Style.RESET_ALL}")

    # Pastikan FFmpeg/FFprobe tersedia sebelum melanjutkan  
    try:  
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)  
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True, text=True)  
    except (subprocess.CalledProcessError, FileNotFoundError):  
        print(f"{Fore.RED}FFmpeg atau FFprobe tidak ditemukan. Tidak dapat membuat video.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")  
        return  

    # --- Pemeriksaan Aset ---
    if not check_required_assets():
        print(f"{Fore.YELLOW}Proses pembuatan video dibatalkan karena aset tidak lengkap.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")
        return
    # --- Akhir Pemeriksaan Aset ---

    renderer = VideoRenderer()  

    project_root = os.path.dirname(BASE_DIR)  

    print(f"\n{Fore.GREEN}--- Pilih File Video ---{Style.RESET_ALL}")  
    media_full_path = os.path.join(project_root, CONFIG['MEDIA_DIR'])  
    available_videos = renderer._show_numbered_files(media_full_path, (".mp4", ".avi", ".mov", ".mkv"))  
    
    if not available_videos:  
        print(f"{Fore.YELLOW}Tidak ada file video ditemukan di {CONFIG['MEDIA_DIR']}.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")  
        return  

    # Tambahkan opsi "0. Batal"
    print(f"{Fore.RED}0. Batal{Style.RESET_ALL}")
    video_choice = input(f"{Fore.CYAN}Pilih nomor video: {Style.RESET_ALL}").strip()  

    if video_choice == '0':
        print(f"{Fore.YELLOW}Pemilihan video dibatalkan.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")
        return # Kembali ke generate_video_submenu
    
    selected_video_path = available_videos.get(video_choice)  

    if not selected_video_path:  
        print(f"{Fore.RED}Pilihan video tidak valid.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")  
        return # Kembali ke generate_video_submenu

    print(f"\n{Fore.GREEN}--- Pilih File Audio ---{Style.RESET_ALL}")  
    music_full_path = os.path.join(project_root, CONFIG['MUSIC_DIR'])  
    available_audio = renderer._show_numbered_files(music_full_path, (".mp3", ".wav", ".aac"))  
    
    if not available_audio:  
        print(f"{Fore.YELLOW}Tidak ada file audio ditemukan di {CONFIG['MUSIC_DIR']}.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")  
        return  

    # Tambahkan opsi "0. Batal"
    print(f"{Fore.RED}0. Batal{Style.RESET_ALL}")
    audio_choice = input(f"{Fore.CYAN}Pilih nomor audio: {Style.RESET_ALL}").strip()  

    if audio_choice == '0':
        print(f"{Fore.YELLOW}Pemilihan audio dibatalkan.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")
        return # Kembali ke generate_video_submenu

    selected_audio_path = available_audio.get(audio_choice)  

    if not selected_audio_path:  
        print(f"{Fore.RED}Pilihan audio tidak valid.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")  
        return # Kembali ke generate_video_submenu

    # --- Konfirmasi Render ---  
    clear_screen()
    print(f"{Fore.CYAN}=== KONFIRMASI GENERATE VIDEO ==={Style.RESET_ALL}")  
    print(f"{Fore.BLUE}Video Terpilih: {os.path.basename(selected_video_path)}{Style.RESET_ALL}")  
    print(f"{Fore.BLUE}Audio Terpilih: {os.path.basename(selected_audio_path)}{Style.RESET_ALL}")  
    print(f"\n{Fore.YELLOW}Apakah Anda ingin melanjutkan proses generate video?{Style.RESET_ALL}")  
    print(f"1. Lanjutkan")  
    print(f"0. Batal")  

    confirm_choice = input(f"{Fore.CYAN}Pilih opsi (1/0): {Style.RESET_ALL}").strip()  

    if confirm_choice == '0':  
        print(f"{Fore.YELLOW}Proses generate video dibatalkan.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")  
        return  
    elif confirm_choice != '1':  
        print(f"{Fore.RED}Pilihan tidak valid. Proses dibatalkan.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")  
        return  
    # --- Akhir Konfirmasi Render ---  

    # Panggil metode render dari VideoRenderer
    # Pesan progres akan ditangani di dalam VideoRenderer._run_ffmpeg_with_progress
    rendered_output_file = renderer.render(selected_video_path, selected_audio_path)  

    if rendered_output_file:  
        relative_output_path = os.path.relpath(rendered_output_file, project_root)  
        print(f"\n{Fore.GREEN}Video berhasil dibuat: {relative_output_path}{Style.RESET_ALL}")  
    else:  
        print(f"\n{Fore.RED}Gagal membuat video.{Style.RESET_ALL}")  
      
    input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")

def batch_generate_videos_process():
    clear_screen()
    print(f"{Fore.CYAN}=== GENERATE VIDEO BATCH (RANDOM) ==={Style.RESET_ALL}")

    # Pastikan FFmpeg/FFprobe tersedia sebelum melanjutkan  
    try:  
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)  
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True, text=True)  
    except (subprocess.CalledProcessError, FileNotFoundError):  
        print(f"{Fore.RED}FFmpeg atau FFprobe tidak ditemukan. Tidak dapat membuat video.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")  
        return  

    # --- Pemeriksaan Aset ---
    if not check_required_assets():
        print(f"{Fore.YELLOW}Proses pembuatan video batch dibatalkan karena aset tidak lengkap.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")
        return
    # --- Akhir Pemeriksaan Aset ---

    renderer = VideoRenderer()  
    project_root = os.path.dirname(BASE_DIR)  

    media_full_path = os.path.join(project_root, CONFIG['MEDIA_DIR'])  
    music_full_path = os.path.join(project_root, CONFIG['MUSIC_DIR'])  

    # Dapatkan daftar path video dan audio yang sebenarnya (bukan map bernomor)
    # _show_numbered_files akan mengembalikan map, kita hanya butuh values-nya
    all_videos_paths = list(renderer._show_numbered_files(media_full_path, (".mp4", ".avi", ".mov", ".mkv")).values())
    all_audio_paths = list(renderer._show_numbered_files(music_full_path, (".mp3", ".wav", ".aac")).values())

    if not all_videos_paths:
        print(f"{Fore.YELLOW}Tidak ada file video tersedia untuk batch generation di {CONFIG['MEDIA_DIR']}.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")
        return
    if not all_audio_paths:
        print(f"{Fore.YELLOW}Tidak ada file audio tersedia untuk batch generation di {CONFIG['MUSIC_DIR']}.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")
        return

    num_videos_to_generate = 0
    while True:
        try:
            num_input = input(f"{Fore.CYAN}Masukkan jumlah video yang akan digenerasi (misal: 3): {Style.RESET_ALL}").strip()
            if num_input == '0': # Opsi batal untuk batch
                print(f"{Fore.YELLOW}Generasi batch dibatalkan.{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu sebelumnya...{Style.RESET_ALL}")
                return
            
            num_videos_to_generate = int(num_input)
            if num_videos_to_generate <= 0:
                print(f"{Fore.RED}Jumlah harus lebih besar dari 0.{Style.RESET_ALL}")
            else:
                break
        except ValueError:
            print(f"{Fore.RED}Masukan tidak valid. Harap masukkan angka atau '0' untuk batal.{Style.RESET_ALL}")

    print(f"\n{Fore.BLUE}Memulai generasi batch {num_videos_to_generate} video...{Style.RESET_ALL}")
    
    generated_count = 0
    failed_count = 0

    for i in range(1, num_videos_to_generate + 1):
        selected_video_path = random.choice(all_videos_paths)
        selected_audio_path = random.choice(all_audio_paths)

        print(f"\n{Fore.CYAN}--- GENERASI VIDEO {i}/{num_videos_to_generate} ---{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Video: {os.path.basename(selected_video_path)}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Audio: {os.path.basename(selected_audio_path)}{Style.RESET_ALL}")

        rendered_output_file = renderer.render(selected_video_path, selected_audio_path)

        if rendered_output_file:
            relative_output_path = os.path.relpath(rendered_output_file, project_root)
            print(f"\n{Fore.GREEN}✓ Video {i} berhasil dibuat: {relative_output_path}{Style.RESET_ALL}")
            generated_count += 1
        else:
            print(f"\n{Fore.RED}✗ Gagal membuat video {i}.{Style.RESET_ALL}")
            failed_count += 1
        time.sleep(1) # Jeda sebentar antar generasi

    print(f"\n{Fore.CYAN}=== GENERASI BATCH SELESAI ==={Style.RESET_ALL}")
    print(f"{Fore.GREEN}Total berhasil: {generated_count}{Style.RESET_ALL}")
    if failed_count > 0:
        print(f"{Fore.RED}Total gagal: {failed_count}{Style.RESET_ALL}")
    input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu utama...{Style.RESET_ALL}")

def reset_overlay_files():
    clear_screen()
    print(f"{Fore.CYAN}=== RESET FILE CAPTION & TREN ==={Style.RESET_ALL}")
    project_root = os.path.dirname(BASE_DIR)
    overlay_base_path = os.path.join(project_root, 'overlay')

    # Daftar file yang akan dihapus
    files_to_delete = [
        os.path.join(overlay_base_path, os.path.basename(CONFIG.get('CAPTION_JSON', 'caption.json'))),
        os.path.join(overlay_base_path, os.path.basename(CONFIG.get('CAPTION_TXT', 'caption.txt'))),
        os.path.join(overlay_base_path, os.path.basename(CONFIG.get('TREND_CACHE_FILE', 'trend_cache.json'))),
        os.path.join(overlay_base_path, os.path.basename(CONFIG.get('TREND_TXT', 'trend.txt')))
    ]

    print(f"\n{Fore.YELLOW}Apakah Anda yakin ingin menghapus semua file berikut?{Style.RESET_ALL}")
    for f_path in files_to_delete:
        print(f"- {os.path.relpath(f_path, project_root)}")
    
    print(f"\n{Fore.RED}Tindakan ini tidak dapat dibatalkan!{Style.RESET_ALL}")
    confirm = input(f"{Fore.CYAN}Ketik 'YA' untuk melanjutkan atau lainnya untuk membatalkan: {Style.RESET_ALL}").strip().upper()

    if confirm == 'YA':
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"{Fore.GREEN}✓ Berhasil menghapus: {os.path.basename(file_path)}{Style.RESET_ALL}")
                    deleted_count += 1
                else:
                    print(f"{Fore.YELLOW}File tidak ditemukan (sudah dihapus atau tidak ada): {os.path.basename(file_path)}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Gagal menghapus {os.path.basename(file_path)}: {e}{Style.RESET_ALL}")
                import traceback
                traceback.print_exc()
        
        if deleted_count > 0:
            print(f"\n{Fore.GREEN}Proses reset selesai. {deleted_count} file berhasil dihapus.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Tidak ada file yang dihapus atau semua sudah tidak ada.{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}Proses reset dibatalkan.{Style.RESET_ALL}")
    
    input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")


def display_trends_from_file():
    clear_screen()
    print(f"{Fore.CYAN}=== DAFTAR TREN ==={Style.RESET_ALL}")
    project_root = os.path.dirname(BASE_DIR)
    
    # Path untuk caption.json (tempat caption yang sudah di-styling disimpan)
    overlay_base_path = os.path.join(project_root, 'overlay')
    caption_json_filename = os.path.basename(CONFIG.get('CAPTION_JSON', 'caption.json'))
    caption_json_path = os.path.join(overlay_base_path, caption_json_filename)

    captions = []
    if not os.path.exists(caption_json_path):
        print(f"{Fore.YELLOW}File caption tidak ditemukan di: {os.path.relpath(caption_json_path, project_root)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Silakan ambil tren terlebih dahulu melalui 'Fetch trend to Captions'.{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")
        return

    try:
        with open(caption_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ambil hanya teks caption dari setiap objek
            captions = [item['text'] for item in data if 'text' in item]
          
        if captions:
            print(f"{Fore.BLUE}(Menampilkan caption yang sudah di-styling dari {os.path.basename(caption_json_path)}){Style.RESET_ALL}\n")
            for i, caption in enumerate(captions, 1):
                print(f"{i}. {caption}\n")
        else:
            print(f"{Fore.YELLOW}Tidak ada tren (caption) yang tersimpan.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Silakan ambil tren dan buat caption terlebih dahulu.{Style.RESET_ALL}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"{Fore.RED}Error membaca atau memparsing {os.path.basename(caption_json_path)}: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Pastikan file tersebut valid JSON dan berisi data caption.{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
      
    input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")

def display_captions_from_file():
    clear_screen()
    print(f"{Fore.CYAN}=== DAFTAR CAPTION ==={Style.RESET_ALL}")
    project_root = os.path.dirname(BASE_DIR)
    
    # Pastikan path caption juga menggunakan base overlay yang benar
    overlay_base_path = os.path.join(project_root, 'overlay')
    caption_json_filename = os.path.basename(CONFIG.get('CAPTION_JSON', 'caption.json'))
    caption_txt_filename = os.path.basename(CONFIG.get('CAPTION_TXT', 'caption.txt'))

    caption_json_path = os.path.join(overlay_base_path, caption_json_filename)
    caption_txt_path = os.path.join(overlay_base_path, caption_txt_filename)

    captions = []  
      
    # Coba baca dari JSON dulu  
    if os.path.exists(caption_json_path):  
        try:  
            with open(caption_json_path, 'r', encoding='utf-8') as f:  
                data = json.load(f)  
                captions = [item['text'] for item in data if 'text' in item]  
        except (json.JSONDecodeError, KeyError) as e:  
            print(f"{Fore.YELLOW}Peringatan: Gagal membaca {os.path.relpath(caption_json_path, project_root)} atau format tidak sesuai: {e}. Mencoba dari .txt.{Style.RESET_ALL}")  
      
    # Fallback ke TXT jika JSON gagal atau kosong  
    if not captions and os.path.exists(caption_txt_path):  
        try:  
            with open(caption_txt_path, 'r', encoding='utf-8') as f:  
                captions = [line.strip() for line in f if line.strip()]  
        except Exception as e:  
            print(f"{Fore.RED}Error membaca file caption TXT: {e}{Style.RESET_ALL}")  
            import traceback  
            traceback.print_exc()  

    if captions:  
        for i, caption in enumerate(captions, 1):  
            print(f"{i}. {caption}\n")  
    else:  
        print(f"{Fore.YELLOW}Tidak ada caption yang tersimpan.{Style.RESET_ALL}")  
        print(f"{Fore.YELLOW}Silakan ambil tren dan buat caption terlebih dahulu.{Style.RESET_ALL}")  
      
    input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")

def trend_and_caption_menu():
    while True:
        clear_screen()
        print(f"{Fore.CYAN}=== TREND & CAPTION ==={Style.RESET_ALL}")
        print(f"1. Fetch trend to Captions")
        print(f"2. View trends")
        print(f"3. View captions")
        print(f"4. Reset (Hapus File Caption & Tren)")
        print(f"{Fore.RED}0. Kembali ke Menu Utama{Style.RESET_ALL}")

        choice = input(f"{Fore.CYAN}Pilih opsi: {Style.RESET_ALL}").strip()  

        if choice == '1':  
            print(f"\n{Fore.BLUE}--- Pilih Gaya Caption ---{Style.RESET_ALL}")  
            print(f"1. poetic")  
            print(f"2. hacker")  
            print(f"3. lintas")  
            print(f"4. nalar (default)")  
            print(f"5. Mix (Acak dari semua gaya)")
            style_choice_num = input(f"{Fore.CYAN}Pilih nomor gaya (1-5, default 4): {Style.RESET_ALL}").strip()  
              
            style_mapping = {  
                '1': 'poetic',  
                '2': 'hacker',  
                '3': 'lintas',  
                '4': 'nalar',
                '5': 'mix'
            }  
            style_name = style_mapping.get(style_choice_num, 'nalar')  
            
            try:  
                generated_captions = update_trends(style_name)  
                if generated_captions:  
                    print(f"\n{Fore.GREEN}Berhasil menghasilkan {len(generated_captions)} caption.{Style.RESET_ALL}")  
                else:  
                    print(f"{Fore.YELLOW}Tidak ada caption yang dihasilkan.{Style.RESET_ALL}")  
            except Exception as e:  
                print(f"{Fore.RED}Terjadi kesalahan saat mengambil tren/caption: {e}{Style.RESET_ALL}")  
                import traceback  
                traceback.print_exc()  
            input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan...{Style.RESET_ALL}")  
          
        elif choice == '2':  
            display_trends_from_file()  
          
        elif choice == '3':  
            display_captions_from_file()  
        
        elif choice == '4':
            reset_overlay_files()
          
        elif choice == '0':  
            break  
          
        else:  
            print(f"{Fore.RED}Pilihan tidak valid. Silakan coba lagi.{Style.RESET_ALL}")  
            time.sleep(1)

def main_menu_app():
    while True:
        clear_screen()
        terminal_width = min(shutil.get_terminal_size().columns, 80)
        divider = '=' * terminal_width
        title = "🎬 ViGE VIDEO GENERATOR PRO".center(terminal_width)
        
        print(f"\n{Fore.CYAN}{divider}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{divider}{Style.RESET_ALL}\n")

        print(f"1. Trend & Caption")
        print(f"2. Pengaturan Aplikasi")
        print(f"3. Buat Video")
        print(f"4. Opsi Visual (Font, Warna, Animasi, dll.)")
        print(f"{Fore.RED}0. Keluar{Style.RESET_ALL}")

        choice = input(f"{Fore.CYAN}Pilih opsi: {Style.RESET_ALL}").strip()  

        if choice == '1':  
            trend_and_caption_menu()  

        elif choice == '2':  
            configure_settings()  
          
        elif choice == '3':  
            generate_video_submenu()

        elif choice == '4':  
            configure_visual_options()  

        elif choice == '0':  
            print(f"{Fore.BLUE}Terima kasih telah menggunakan ViGE! Sampai jumpa.{Style.RESET_ALL}")  
            sys.exit()  
          
        else:  
            print(f"{Fore.RED}Pilihan tidak valid. Silakan coba lagi.{Style.RESET_ALL}")  
            time.sleep(1)

def main():
    clear_screen()
    print(f"{Fore.BLUE}Starting ViGE - Video Generator Engine (Mode Teks & Caption){Style.RESET_ALL}")
    print(f"{Fore.CYAN}Melakukan pemeriksaan sistem awal...{Style.RESET_ALL}")

    if not validate_environment():  
        print(f"\n{Fore.RED}Aplikasi tidak dapat berjalan tanpa FFmpeg/FFprobe. Silakan instal terlebih dahulu.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk keluar...{Style.RESET_ALL}")  
        sys.exit(1)  
      
    create_directories()  

    if not check_dependencies():  
        print(f"\n{Fore.RED}File-file penting tidak lengkap. Aplikasi tidak dapat berjalan.{Style.RESET_ALL}")  
        input(f"{Fore.CYAN}Tekan ENTER untuk keluar...{Style.RESET_ALL}")  
        sys.exit(1)  
      
    try:  
        load_config()  
        print(f"{Fore.GREEN}✓ Konfigurasi dimuat berhasil.{Style.RESET_ALL}")  
    except Exception as e:  
        print(f"{Fore.RED}Error memuat konfigurasi: {e}. Menggunakan konfigurasi default.{Style.RESET_ALL}")  
        import traceback  
        traceback.print_exc()  
          
    print(f"{Fore.GREEN}✓ Semua pemeriksaan awal selesai. Memuat aplikasi utama...{Style.RESET_ALL}")  
    time.sleep(1)  

    logged_in = False  
    while not logged_in:  
        clear_screen()
        print(f"{Fore.MAGENTA}=== PILIH MODE LOGIN ==={Style.RESET_ALL}")  
        print(f"{Fore.YELLOW}1. User (Membutuhkan Lisensi Key){Style.RESET_ALL}")  
        print(f"{Fore.YELLOW}2. Developer Mode (Tanpa Verifikasi Lisensi){Style.RESET_ALL}")  
          
        choice = input(f"{Fore.CYAN}Masukkan pilihan Anda (1/2): {Style.RESET_ALL}").strip()  

        if choice == '1':  
            print(f"\n{Fore.BLUE}Memilih mode User. Memverifikasi lisensi...{Style.RESET_ALL}")  
            # Pastikan modules.license diimpor di sini atau di awal file
            from modules.license import display_licence_info  
            if display_licence_info():  
                logged_in = True  
                print(f"{Fore.GREEN}Lisensi berhasil diverifikasi. Melanjutkan ke aplikasi...{Style.RESET_ALL}")  
            else:  
                print(f"{Fore.RED}Verifikasi lisensi gagal. Silakan coba lagi atau hubungi dukungan.{Style.RESET_ALL}")  
                input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu login...{Style.RESET_ALL}")  
        elif choice == '2':  
            print(f"\n{Fore.BLUE}Memilih Developer Mode. Melanjutkan tanpa verifikasi lisensi...{Style.RESET_ALL}")  
            logged_in = True  
        else:  
            print(f"{Fore.RED}Pilihan tidak valid. Silakan masukkan '1' atau '2'.{Style.RESET_ALL}")  
            input(f"{Fore.CYAN}Tekan ENTER untuk kembali ke menu login...{Style.RESET_ALL}")  

    try:  
        main_menu_app()  
              
    except ImportError as e:  
        print(f"\n{Fore.RED}Import Error: {str(e)}{Style.RESET_ALL}")  
        print(f"{Fore.YELLOW}Kemungkinan masalah:{Style.RESET_ALL}")  
        print("- Ada file modul yang belum lengkap atau namanya salah.")  
        print("- Ada syntax error di salah satu modul.")  
        print("- Struktur folder tidak sesuai (misal: 'modules' tidak ada atau salah nama).")  
        print(f"Periksa kembali file-es di '{os.path.join(BASE_DIR, 'modules')}'")  
    except Exception as e:  
        print(f"\n{Fore.RED}Kesalahan tak terduga terjadi: {type(e).__name__}: {str(e)}{Style.RESET_ALL}")  
        import traceback  
        traceback.print_exc()  
    finally:  
        input(f"{Fore.CYAN}Tekan ENTER untuk keluar...{Style.RESET_ALL}")

if __name__ == "__main__": # Perbaikan: menggunakan __name__
    main()
