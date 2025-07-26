import os
import random
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from colorama import Fore, Style
import re
import time
import sys
import threading

from modules.config import CONFIG  # Import at top level

class VideoRenderer:
    def __init__(self):
        # Menggunakan __file__ untuk mendapatkan path absolut dari file video_renderer.py
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.media_dir = os.path.join(self.project_root, CONFIG.get('MEDIA_DIR', 'assets/media'))  
        self.music_dir = os.path.join(self.project_root, CONFIG.get('MUSIC_DIR', 'assets/music'))  
          
        self.font_dir_full_path = os.path.join(self.project_root, CONFIG.get('FONT_DIR', 'assets/font'))  
        self.font_path = self._get_random_font_path(self.font_dir_full_path)  
          
        # Menggunakan resolusi dari CONFIG jika ada, default ke 1080x1920
        self.output_width = CONFIG.get('VIDEO_WIDTH', 1080)  
        self.output_height = CONFIG.get('VIDEO_HEIGHT', 1920)  
        
        # Path overlay yang benar, selalu dari project_root dan 'overlay'
        self.overlay_dir = os.path.join(self.project_root, 'overlay')  
        self.output_dir = os.path.join(self.project_root, CONFIG.get('OUTPUT_DIR', 'output'))  

        # Direktori sementara baru (sekarang tersembunyi)
        self.tmp_dir = os.path.join(self.project_root, '.tmp') # Mengubah nama direktori menjadi .tmp

        # Pastikan direktori-direktori ini ada
        os.makedirs(self.output_dir, exist_ok=True)  
        os.makedirs(self.overlay_dir, exist_ok=True)  
        os.makedirs(self.tmp_dir, exist_ok=True) # Buat direktori .tmp jika belum ada

        self.total_duration = 0  
        self.start_time = 0  

    def _get_random_font_path(self, font_directory):  
        available_fonts = []  
        if not os.path.exists(font_directory):  
            print(f"{Fore.YELLOW}Peringatan: Direktori font tidak ditemukan: {font_directory}. Menggunakan font sistem default.{Style.RESET_ALL}")  
            return "sans-serif"  

        for root, _, files in os.walk(font_directory):  
            for file in files:  
                if file.lower().endswith(('.ttf', '.otf')):  
                    available_fonts.append(os.path.join(root, file))  
          
        if available_fonts:  
            selected_font = random.choice(available_fonts)  
            print(f"{Fore.GREEN}✓ Font dipilih secara acak: {os.path.basename(selected_font)}{Style.RESET_ALL}")  
            return selected_font  
        else:  
            print(f"{Fore.YELLOW}Peringatan: Tidak ada file font (.ttf/.otf) ditemukan di {font_directory}. Menggunakan font sistem default.{Style.RESET_ALL}")  
            return "sans-serif"  

    def _generate_filename(self):  
        now = datetime.now()  
        # Format nama file yang lebih deskriptif
        return os.path.join(self.output_dir, f"ViGE_Content_{now.strftime('%Y%m%d_%H%M%S')}.mp4")

    def _show_numbered_files(self, directory, extensions):
        """Menampilkan daftar file bernomor di direktori tertentu."""
        try:
            files = sorted([f for f in os.listdir(directory) 
                          if f.lower().endswith(extensions)])
            if not files:
                # Mengubah ini menjadi pesan peringatan daripada raise error
                # Untuk batch, kita hanya ingin daftar path, bukan pesan ke user
                # Pesan akan ditangani di batch_generate_videos_process
                return {}

            # Untuk mode kustom, tetap tampilkan daftar bernomor
            # sys._getframe(1).f_code.co_name == 'generate_video_process' adalah cara yang kurang robust
            # Lebih baik menggunakan parameter eksplisit jika memungkinkan,
            # tetapi untuk kasus ini, ini adalah solusi cepat.
            calling_function_name = sys._getframe(1).f_code.co_name
            if calling_function_name == 'generate_video_process':
                print(f"{Fore.YELLOW}File yang tersedia:{Style.RESET_ALL}")
                file_map = {}
                for i, file in enumerate(files, 1):
                    file_path = os.path.join(directory, file)
                    print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {file}")
                    file_map[str(i)] = file_path
                return file_map
            else: # Untuk batch, hanya kembalikan path
                return {str(i): os.path.join(directory, file) for i, file in enumerate(files, 1)}
            
        except Exception as e:
            print(f"{Fore.RED}Error saat menampilkan file dari {directory}: {e}{Style.RESET_ALL}")
            return {}

    def _get_media_duration(self, media_path):
        """Mendapatkan durasi media (video/audio) untuk pelacakan progres."""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                media_path
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return float(result.stdout)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Tidak dapat mendapatkan durasi media {os.path.basename(media_path)}: {e}{Style.RESET_ALL}")
            return None

    def _run_ffmpeg_with_progress(self, cmd, total_duration=None, step_name="Processing"):
        """Menjalankan FFmpeg dengan pelacakan progres, menimpa baris."""
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        start_time = time.time()
        
        # Pindah ke baris baru untuk progres, memastikan tidak menumpuk dengan output sebelumnya
        sys.stdout.write("\n") 
        sys.stdout.flush()

        # Regex untuk menangkap waktu dari output FFmpeg
        time_regex = re.compile(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})")
        # Regex untuk menangkap frame dari output FFmpeg (fallback)
        frame_regex = re.compile(r"frame=\s*(\d+)")

        while True:
            # Baca baris demi baris dari stderr
            line = process.stderr.readline()
            
            # Jika tidak ada baris lagi dan proses sudah selesai, keluar
            if not line and process.poll() is not None:
                break
            
            # Jika tidak ada baris tapi proses masih berjalan, tunggu sebentar
            if not line:
                time.sleep(0.05) # Hindari busy-waiting
                continue
                
            # Coba cocokkan dengan regex waktu
            time_match = time_regex.search(line)
            if time_match:
                time_str = time_match.group(1)
                h, m, s = map(float, time_str.split(':'))
                current_time = h * 3600 + m * 60 + s
                
                if total_duration and total_duration > 0:
                    percent = min(100, (current_time / total_duration) * 100)
                    elapsed_time = time.time() - start_time
                    
                    # Estimasi waktu tersisa
                    if percent > 0:
                        estimated_total_time = elapsed_time / (percent / 100)
                        time_left = estimated_total_time - elapsed_time
                    else:
                        time_left = float('inf') # Tidak bisa mengestimasi jika progres 0
                    
                    # Clear baris dan cetak ulang
                    sys.stdout.write(f"\r{Fore.MAGENTA}{step_name}: {percent:.1f}% | Time left: {time_left:.1f}s{Style.RESET_ALL}")
                    sys.stdout.flush()
            # Fallback jika tidak ada 'time=' tapi ada 'frame=' (misalnya saat encoding ulang)
            elif total_duration is None and frame_regex.search(line):
                frame_match = frame_regex.search(line)
                if frame_match:
                    current_frame = int(frame_match.group(1))
                    sys.stdout.write(f"\r{Fore.MAGENTA}{step_name}: Frame {current_frame}{Style.RESET_ALL}")
                    sys.stdout.flush()
            # Jika baris bukan progres, kita bisa memilih untuk mengabaikannya atau mencetaknya
            # Untuk menghindari penumpukan, kita akan mengabaikan baris yang tidak relevan dengan progres
            # Atau bisa juga menambahkan logika untuk mencetak baris penting saja (misal error)

        # Pastikan kursor di baris baru setelah progres selesai
        sys.stdout.write("\n")
        sys.stdout.flush()
        
        return process.wait()

    def _get_random_caption(self):
        """Membaca dan mengembalikan satu caption acak dari overlay/caption.json atau caption.txt."""
        # Pastikan path ke caption selalu dari project_root dan 'overlay'
        overlay_base_path = os.path.join(self.project_root, 'overlay')
        
        # Gunakan os.path.basename untuk memastikan kita hanya mendapatkan nama file dari CONFIG
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
                    if any(item.get('text') for item in data): # Cek apakah ada caption valid
                        captions = [item['text'] for item in data if 'text' in item]
            except (json.JSONDecodeError, KeyError):
                pass # Lanjut cek TXT jika JSON error
        
        # Fallback ke TXT jika JSON gagal atau kosong
        if not captions and os.path.exists(caption_txt_path):
            try:
                with open(caption_txt_path, 'r', encoding='utf-8') as f:
                    captions = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"{Fore.RED}Error membaca file caption TXT: {e}{Style.RESET_ALL}")
                return "Default Caption" # Fallback jika terjadi error
        
        if captions:
            return random.choice(captions)
        else:
            # Menggunakan os.path.relpath untuk pesan yang lebih bersih
            print(f"{Fore.YELLOW}Tidak ada caption ditemukan di {os.path.relpath(caption_json_path, self.project_root)} atau {os.path.relpath(caption_txt_path, self.project_root)}. Menggunakan caption default.{Style.RESET_ALL}")
            return "ViGE - Your Daily Dose of Inspiration"

    def render(self, video_path, audio_path):
        """Main rendering pipeline dengan pelacakan progres."""
        output_file_name = self._generate_filename()
        
        # Path file sementara, sekarang di dalam direktori .tmp
        processed_video_temp = os.path.join(self.tmp_dir, "temp_vertical.mp4")
        merged_video_temp = os.path.join(self.tmp_dir, "temp_merged.mp4")

        try:
            # 1. Proses video dengan progres (scaling/padding)
            original_video_duration = self._get_media_duration(video_path)
            if original_video_duration is None:
                print(f"{Fore.YELLOW}Tidak dapat menentukan durasi video asli, progres mungkin tidak akurat untuk langkah ini.{Style.RESET_ALL}")
                original_video_duration = 30 # Fallback duration

            cmd_process_video = [
                "ffmpeg",
                "-y", # Overwrite output files without asking
                "-i", video_path,
                "-vf", f"scale={self.output_width}:{self.output_height}:force_original_aspect_ratio=decrease,pad={self.output_width}:{self.output_height}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                "-c:v", "libx264", # Menggunakan H.264 codec
                "-preset", "medium", # Preset untuk keseimbangan kecepatan/kualitas
                "-crf", "23", # Constant Rate Factor untuk kualitas (23 adalah default yang baik)
                "-c:a", "aac", # Menggunakan AAC codec untuk audio
                "-b:a", "192k", # Bitrate audio
                processed_video_temp
            ]
            
            print(f"\n{Fore.BLUE}Mengonversi video ke HD vertikal...{Style.RESET_ALL}")
            result = self._run_ffmpeg_with_progress(cmd_process_video, original_video_duration, "Video Conversion")
            
            if result != 0:
                print(f"\n{Fore.RED}Gagal mengonversi video.{Style.RESET_ALL}")
                return None
            print(f"\n{Fore.GREEN}✓ Konversi video selesai.{Style.RESET_ALL}")

            # 2. Gabungkan dengan audio
            # Durasi video yang sudah diproses (temp_vertical.mp4) akan menjadi durasi untuk langkah ini
            processed_video_duration = self._get_media_duration(processed_video_temp)
            if processed_video_duration is None:
                print(f"{Fore.YELLOW}Tidak dapat menentukan durasi video yang diproses, progres mungkin tidak akurat untuk penggabungan.{Style.RESET_ALL}")
                processed_video_duration = 30 # Fallback

            print(f"\n{Fore.BLUE}Menggabungkan audio...{Style.RESET_ALL}")
            cmd_merge = [
                "ffmpeg",
                "-y",
                "-i", processed_video_temp,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest", # Memotong video/audio agar sesuai dengan yang terpendek
                merged_video_temp
            ]
            # Gunakan _run_ffmpeg_with_progress untuk langkah ini juga
            result = self._run_ffmpeg_with_progress(cmd_merge, processed_video_duration, "Audio Merging")
            if result != 0:
                print(f"\n{Fore.RED}Gagal menggabungkan audio.{Style.RESET_ALL}")
                return None
            print(f"\n{Fore.GREEN}✓ Penggabungan audio selesai.{Style.RESET_ALL}")

            # 3. Tambahkan caption
            # Durasi video yang sudah digabungkan (temp_merged.mp4) akan menjadi durasi untuk langkah ini
            merged_video_duration = self._get_media_duration(merged_video_temp)
            if merged_video_duration is None:
                print(f"{Fore.YELLOW}Tidak dapat menentukan durasi video yang digabungkan, progres mungkin tidak akurat untuk caption.{Style.RESET_ALL}")
                merged_video_duration = 30 # Fallback

            print(f"\n{Fore.BLUE}Menambahkan caption...{Style.RESET_ALL}")
            caption_text = self._get_random_caption()
            
            # Escape karakter khusus untuk FFmpeg drawtext
            # Ganti ' menjadi \\' dan : menjadi \:
            escaped_caption = caption_text.replace("'", "\\'").replace(":", "\\:").replace("\\", "\\\\")

            # Menggunakan font_path yang sudah diinisialisasi
            # Pastikan font_path di-escape jika mengandung karakter khusus atau spasi
            escaped_font_path = self.font_path.replace("\\", "/").replace(":", "\\:")

            # Menentukan ukuran font berdasarkan lebar video
            # Contoh: 5% dari lebar video
            font_size = int(self.output_width * 0.05) 
            
            # Posisi caption: 5% dari tinggi dari bawah
            y_position = f"h-th-{int(self.output_height * 0.05)}" 

            cmd_caption = [
                "ffmpeg",
                "-y",
                "-i", merged_video_temp,
                "-vf", f"drawtext=text='{escaped_caption}':fontfile='{escaped_font_path}':fontsize={font_size}:x=(w-tw)/2:y={y_position}:fontcolor=white:bordercolor=black:borderw=2",
                "-c:a", "copy",
                output_file_name
            ]
            # Gunakan _run_ffmpeg_with_progress untuk langkah ini juga
            result = self._run_ffmpeg_with_progress(cmd_caption, merged_video_duration, "Adding Caption")
            if result != 0:
                print(f"\n{Fore.RED}Gagal menambahkan caption.{Style.RESET_ALL}")
                return None
            print(f"{Fore.GREEN}✓ Penambahan caption selesai.{Style.RESET_ALL}")

            # Cleanup file sementara
            for temp_file in [processed_video_temp, merged_video_temp]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return output_file_name
            
        except subprocess.CalledProcessError as e:
            print(f"\n{Fore.RED}Render Error: FFmpeg command failed.{Style.RESET_ALL}")
            if e.stdout:
                print(f"{Fore.RED}STDOUT: {e.stdout.decode()}{Style.RESET_ALL}")
            if e.stderr:
                print(f"{Fore.RED}STDERR: {e.stderr.decode()}{Style.RESET_ALL}")
            # Cleanup temp files even on error
            for temp_file in [processed_video_temp, merged_video_temp]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return None
        except FileNotFoundError as e:
            print(f"\n{Fore.RED}Error: FFmpeg atau file input tidak ditemukan. Pastikan FFmpeg terinstal dan path file benar. {e}{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"\n{Fore.RED}Kesalahan tak terduga saat rendering: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return None
