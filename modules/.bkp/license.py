# modules/license.py - VERSI FINAL UNTUK KOMUNIKASI DENGAN SERVER

import os
import hashlib
import time
import json
import base64
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import requests # Tambahkan ini untuk HTTP requests

init(autoreset=True)

# Lokasi file lisensi
LICENSE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'license.key')
USAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'usage.log')

# --- KONFIGURASI PENTING ---
# GANTI INI DENGAN URL FLASK_APP.PY ANDA DI PYTHONANYWHERE
SERVER_API_URL = "https://jcdou.pythonanywhere.com" # GANTI yourusername!
VALIDATE_ENDPOINT = f"{SERVER_API_URL}/validate_license"
# --- AKHIR KONFIGURASI ---

def clear_screen():
    """Membersihkan layar konsol."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_device_id():
    """
    Mengambil Device ID unik dari perangkat Termux.
    Untuk kesederhanaan dan keandalan yang lebih baik di Termux,
    kita bisa menggunakan kombinasi informasi perangkat yang stabil.
    """
    try:
        # Coba gunakan output 'getprop' untuk Android ID (jika tersedia dan konsisten)
        import subprocess
        result = subprocess.run(['getprop', 'ro.boot.serialno'], capture_output=True, text=True, check=False)
        serial_no = result.stdout.strip()
        if serial_no:
            return hashlib.sha256(serial_no.encode('utf-8')).hexdigest()
    except Exception:
        pass # Lanjut ke fallback jika ada error

    # Fallback yang lebih andal dari sebelumnya: hash path aplikasi + nama host
    # Ini akan cukup unik per instalasi Termux
    app_path = os.path.dirname(os.path.abspath(__file__))
    hostname = os.uname().nodename
    
    unique_string = f"{app_path}-{hostname}"
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

def get_current_usage_count():
    """Membaca jumlah penggunaan dari file log."""
    if not os.path.exists(USAGE_FILE):
        return 0
    try:
        with open(USAGE_FILE, 'r') as f:
            lines = f.readlines()
            return len(lines)
    except Exception as e:
        print(f"{Fore.RED}Error membaca log penggunaan: {e}{Style.RESET_ALL}")
        return 0

def increment_usage_count():
    """Menambahkan satu ke jumlah penggunaan."""
    try:
        with open(USAGE_FILE, 'a') as f:
            f.write(f"{datetime.now().isoformat()}\n")
    except Exception as e:
        print(f"{Fore.RED}Error menulis log penggunaan: {e}{Style.RESET_ALL}")

def get_license_info():
    """Membaca kunci lisensi dari file."""
    if not os.path.exists(LICENSE_FILE):
        return None
    try:
        with open(LICENSE_FILE, 'r') as f:
            key = f.read().strip()
            return key
    except Exception as e:
        print(f"{Fore.RED}Error membaca file lisensi: {e}{Style.RESET_ALL}")
        return None

def save_manual_license_key(key):
    """Menyimpan kunci lisensi yang dimasukkan secara manual."""
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            f.write(key.strip())
        print(f"{Fore.GREEN}Kunci lisensi berhasil disimpan.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Gagal menyimpan kunci lisensi: {e}{Style.RESET_ALL}")

def parse_license_key(license_key_str):
    """
    Menganalisis string kunci lisensi dan mengembalikan data yang didekode
    dan status validasi signature.
    Ini adalah fungsi lokal untuk membaca data dari kunci sebelum dikirim ke server.
    """
    prefix = "VIGE-LICENSE-"
    if not license_key_str.startswith(prefix):
        return None, False, "Invalid prefix"

    encoded_data = license_key_str[len(prefix):]
    try:
        decoded_json_str = base64.urlsafe_b64decode(encoded_data).decode('utf-8')
        license_data = json.loads(decoded_json_str)
    except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, False, f"Failed to decode or parse JSON: {e}"

    stored_signature = license_data.get("signature")
    if not stored_signature:
        return license_data, False, "Missing signature"

    data_for_internal_hash = license_data.copy()
    data_for_internal_hash.pop("signature", None)
    
    core_json_data_str = json.dumps(data_for_internal_hash, sort_keys=True)
    calculated_signature = hashlib.sha256(core_json_data_str.encode('utf-8')).hexdigest()

    if calculated_signature != stored_signature:
        return license_data, False, "Signature mismatch"

    return license_data, True, "Signature valid"


def is_license_valid_via_server(license_key, user_email, device_id):
    """
    Memvalidasi kunci lisensi melalui server API.
    """
    payload = {
        "license_key": license_key,
        "device_id": device_id,
        "email": user_email
    }
    try:
        response = requests.post(VALIDATE_ENDPOINT, json=payload, timeout=15)
        response.raise_for_status() # Akan raise HTTPError untuk status kode 4xx/5xx
        
        server_response = response.json()
        return server_response.get("status") == "valid", server_response.get("message", "Unknown server response")
    except requests.exceptions.RequestException as e:
        return False, f"Network or server error: {e}"
    except json.JSONDecodeError:
        return False, f"Invalid JSON response from server: {response.text}"


def display_license_info_summary(key=None, current_user_email=None, current_device_id=None):
    """Menampilkan ringkasan informasi lisensi."""
    current_key = key if key else get_license_info()
    
    print(f"\n{Fore.CYAN}=== RINGKASAN LISENSI ==={Style.RESET_ALL}")
    if current_key:
        license_data, signature_valid, sig_message = parse_license_key(current_key)
        
        # Lakukan validasi via server untuk status akhir
        is_valid_server, validation_message_server = is_license_valid_via_server(current_key, current_user_email, current_device_id)

        print(f"{Fore.BLUE}Kunci Lisensi: {current_key[:40]}...{current_key[-10:]}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Signature Lokal: {'Valid' if signature_valid else 'Invalid'} ({sig_message}){Style.RESET_ALL}")

        if license_data:
            print(f"{Fore.BLUE}Versi: {license_data.get('version', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Diterbitkan: {license_data.get('issued_at', 'N/A').split('T')[0]}{Style.RESET_ALL}")
            
            valid_until_display = "Unlimited"
            if license_data.get("valid_until"):
                try:
                    valid_until_dt = datetime.fromisoformat(license_data["valid_until"])
                    valid_until_display = valid_until_dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    valid_until_display = "Invalid Date"
            print(f"{Fore.BLUE}Valid Hingga (di Kunci): {valid_until_display}{Style.RESET_ALL}")
            
            usage_limit_display = "Unlimited"
            if license_data.get("usage_limit") is not None:
                usage_limit_display = license_data["usage_limit"]
            current_usage = get_current_usage_count()
            print(f"{Fore.BLUE}Penggunaan Lokal: {current_usage}/{usage_limit_display}{Style.RESET_ALL}")

            max_activations_display = "Unlimited"
            if license_data.get("max_activations") is not None:
                max_activations_display = license_data["max_activations"]
            print(f"{Fore.BLUE}Batas Aktivasi: {max_activations_display} perangkat{Style.RESET_ALL}")

            print(f"{Fore.BLUE}Email Terdaftar: {license_data.get('email', 'N/A')}{Style.RESET_ALL}")
            
            # Hanya tampilkan Device ID terdaftar jika ada di license_data (dari generator lama)
            # Karena sekarang server yang melacak Device ID, field ini bisa saja tidak ada di kunci
            # jika generatornya sudah diupdate hanya untuk max_activations
            # if license_data.get('device_id'):
            #     print(f"{Fore.BLUE}Device ID Terdaftar: {license_data.get('device_id', 'N/A')[:8]}...{Style.RESET_ALL}")
            
            if current_user_email:
                print(f"{Fore.BLUE}Email Saat Ini: {current_user_email}{Style.RESET_ALL}")
            if current_device_id:
                print(f"{Fore.BLUE}Device ID Saat Ini: {current_device_id[:8]}...{Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}Data Lisensi Tidak Dapat Diurai Secara Lokal.{Style.RESET_ALL}")

        # Tampilkan status dari server
        if is_valid_server:
            print(f"{Fore.GREEN}Status Lisensi (SERVER): {validation_message_server}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Status Lisensi (SERVER): {validation_message_server}{Style.RESET_ALL}")
            
    else:
        print(f"{Fore.YELLOW}Status: Tidak ada kunci lisensi ditemukan.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}========================={Style.RESET_ALL}")


def display_licence_info():
    """
    Menampilkan informasi lisensi dan meminta pengguna untuk memasukkan atau memverifikasi.
    Mengembalikan True jika valid dan dapat dilanjutkan, False jika tidak.
    """
    current_key = get_license_info()
    
    # Ambil email pengguna (misalnya dari input atau config aplikasi utama)
    current_user_email = input(f"{Fore.WHITE}Masukkan email Anda untuk validasi lisensi: {Style.RESET_ALL}").strip()
    current_device_id = get_device_id() # Dapatkan device ID lokal

    if not current_user_email:
        print(f"{Fore.RED}Email tidak boleh kosong untuk validasi lisensi.{Style.RESET_ALL}")
        time.sleep(2)
        return False

    # Validasi kunci awal (lokal) dan kemudian via server
    local_license_data, local_signature_valid, local_sig_message = parse_license_key(current_key)
    if not local_license_data or not local_signature_valid:
        print(f"{Fore.RED}Kunci lisensi rusak atau tidak valid secara lokal: {local_sig_message}{Style.RESET_ALL}")
        time.sleep(2)
        return False # Jangan lanjutkan ke server jika kunci lokal sudah rusak

    while True:
        clear_screen()
        display_license_info_summary(current_key, current_user_email, current_device_id)
        
        # VALIDASI UTAMA SEKARANG ADA DI SERVER
        is_valid, validation_message = is_license_valid_via_server(current_key, current_user_email, current_device_id)

        if is_valid:
            print(f"{Fore.GREEN}Kunci lisensi Anda valid. {validation_message}{Style.RESET_ALL}")
            choice = input(f"{Fore.CYAN}Tekan ENTER untuk melanjutkan atau (m) untuk menu lisensi: {Style.RESET_ALL}").strip().lower()
            if choice == 'm':
                return handle_license_menu()
            increment_usage_count()
            return True
        else:
            print(f"{Fore.RED}Kunci lisensi Anda tidak valid atau kadaluarsa: {validation_message}{Style.RESET_ALL}")
            
            choice = input(f"{Fore.CYAN}(1) Masukkan kunci lisensi, (m) Menu Lisensi, (x) Keluar: {Style.RESET_ALL}").strip().lower()
            if choice == '1':
                new_key = input(f"{Fore.WHITE}Masukkan kunci lisensi baru: {Style.RESET_ALL}").strip()
                save_manual_license_key(new_key)
                current_key = new_key # Update current_key for next loop iteration
                # Setelah memasukkan kunci baru, kita perlu "memicu" validasi lagi
                # agar update status segera terlihat
                clear_screen()
                display_license_info_summary(current_key, current_user_email, current_device_id)
                is_valid_new_key, validation_message_new_key = is_license_valid_via_server(current_key, current_user_email, current_device_id)
                if is_valid_new_key:
                    print(f"{Fore.GREEN}Kunci baru valid. Melanjutkan...{Style.RESET_ALL}")
                    increment_usage_count()
                    return True
                else:
                    print(f"{Fore.RED}Kunci baru juga tidak valid: {validation_message_new_key}{Style.RESET_ALL}")
                    time.sleep(2) # Beri waktu baca
                    # Lanjutkan loop untuk opsi lagi
            elif choice == 'm':
                return handle_license_menu()
            elif choice == 'x':
                return False
            else:
                print(f"{Fore.RED}Pilihan tidak valid.{Style.RESET_ALL}")
                time.sleep(1)

def handle_license_menu():
    """Menampilkan menu untuk manajemen lisensi."""
    # Untuk menu lisensi, kita tidak perlu email dan device_id untuk ditampilkan
    while True:
        clear_screen()
        # Perhatikan: display_license_info_summary di sini tidak punya email/device_id karena ini di menu
        # Namun, di dalam display_license_info_summary, ia akan mencoba mendapatkan info tsb
        # Ini tradeoff untuk kesederhanaan, jika Anda ingin tampilkan info ini juga di menu,
        # Anda perlu meneruskan parameter email/device_id dari display_licence_info()
        display_license_info_summary() 
        print(f"\n{Fore.CYAN}=== MENU LISENSI ==={Style.RESET_ALL}")
        print(f"1. Masukkan Kunci Lisensi Baru")
        print(f"2. Hapus File Lisensi")
        print(f"3. Reset Penggunaan Lokal (Hanya untuk Debugging/Pengembangan)")
        print(f"{Fore.YELLOW}0. Kembali ke Aplikasi{Style.RESET_ALL}")
        
        choice = input(f"{Fore.CYAN}Pilih opsi: {Style.RESET_ALL}").strip().lower()
        
        if choice == '1':
            new_key = input(f"{Fore.WHITE}Masukkan kunci lisensi baru: {Style.RESET_ALL}").strip()
            save_manual_license_key(new_key)
            # Perhatikan: Setelah menyimpan, kunci ini perlu didaftarkan ke server jika belum ada.
            # Namun, karena ini adalah 'masukkan manual', asumsikan kunci ini sudah terdaftar
            # oleh generate_license_key di sisi dev, atau akan divalidasi oleh server nanti.
        elif choice == '2':
            confirm = input(f"{Fore.YELLOW}Yakin ingin menghapus file lisensi? (y/n): {Style.RESET_ALL}").strip().lower()
            if confirm == 'y':
                delete_license_files()
            time.sleep(1)
        elif choice == '3':
            confirm = input(f"{Fore.YELLOW}Yakin ingin mereset penggunaan lokal? Ini untuk debugging! (y/n): {Style.RESET_ALL}").strip().lower()
            if confirm == 'y':
                if os.path.exists(USAGE_FILE):
                    os.remove(USAGE_FILE)
                    print(f"{Fore.GREEN}Log penggunaan lokal berhasil direset.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}File log penggunaan tidak ditemukan, tidak ada yang perlu direset.{Style.RESET_ALL}")
            time.sleep(1)
        elif choice == '0':
            return True
        else:
            print(f"{Fore.RED}Pilihan tidak valid.{Style.RESET_ALL}")
            time.sleep(1)

def delete_license_files():
    """Menghapus file lisensi dan log penggunaan."""
    if os.path.exists(LICENSE_FILE):
        os.remove(LICENSE_FILE)
        print(f"{Fore.GREEN}File lisensi dihapus.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}File lisensi tidak ditemukan.{Style.RESET_ALL}")
    
    if os.path.exists(USAGE_FILE):
        os.remove(USAGE_FILE)
        print(f"{Fore.GREEN}Log penggunaan dihapus.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Log penggunaan tidak ditemukan.{Style.RESET_ALL}")