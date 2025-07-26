# modules/scraper.py
import requests
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

from modules.config import CONFIG

class Scraper:
    def __init__(self):
        self.config = CONFIG
        self.caption_json_path = os.path.join(self.config['OVERLAY_DIR'], os.path.basename(self.config['CAPTION_JSON']))
        self.caption_txt_path = os.path.join(self.config['OVERLAY_DIR'], os.path.basename(self.config['CAPTION_TXT']))
        self.trend_txt_path = os.path.join(self.config['OVERLAY_DIR'], os.path.basename(self.config['TREND_TXT']))
        self.overlay_dir = self.config['OVERLAY_DIR']

        os.makedirs(self.overlay_dir, exist_ok=True)

    def fetch_data_from_api(self, query):
        """Contoh: Mengambil data dari API eksternal (misal, untuk quotes, facts, dll)."""
        # Ganti dengan API yang sebenarnya dan kunci API jika diperlukan
        api_url = "https://api.example.com/data" 
        headers = {"Authorization": f"Bearer {self.config.get('AIML_API_KEY', 'YOUR_KEY_HERE')}"} 
        params = {"q": query, "limit": 1}

        print(f"{Fore.CYAN}Mengambil data untuk '{query}' dari API...{Style.RESET_ALL}")
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                print(f"{Fore.GREEN}✓ Data berhasil diambil.{Style.RESET_ALL}")
                return data[0]
            else:
                print(f"{Fore.YELLOW}Tidak ada data ditemukan untuk '{query}'.{Style.RESET_ALL}")
                return None
        except requests.RequestException as e:
            print(f"{Fore.RED}✗ Gagal mengambil data dari API: {e}{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}Error saat memproses data API: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return None

    def read_local_quotes(self):
        """Contoh: Membaca quote dari file lokal."""
        quotes_file_path = os.path.join(self.overlay_dir, "quotes.txt")
        print(f"{Fore.CYAN}Membaca quotes dari {quotes_file_path}...{Style.RESET_ALL}")
        if not os.path.exists(quotes_file_path):
            print(f"{Fore.YELLOW}Peringatan: File quotes.txt tidak ditemukan. Buat file ini di {self.overlay_dir} untuk quotes lokal.{Style.RESET_ALL}")
            return []
        try:
            with open(quotes_file_path, 'r', encoding='utf-8') as f:
                quotes = [line.strip() for line in f if line.strip()]
            print(f"{Fore.GREEN}✓ {len(quotes)} quotes ditemukan.{Style.RESET_ALL}")
            return quotes
        except Exception as e:
            print(f"{Fore.RED}✗ Gagal membaca quotes.txt: {e}{Style.RESET_ALL}")
            return []

    def update(self, type="quotes", query=None):
        """
        Fungsi utama untuk mengambil data berdasarkan tipe.
        Mengembalikan data mentah yang diambil.
        """
        print(f"{Fore.CYAN}=== DATA SCRAPER ==={Style.RESET_ALL}")
        
        data_fetched = []
        if type == "quotes":
            data_fetched = self.read_local_quotes()
            if not data_fetched and query: # Coba ambil dari API jika ada query dan lokal kosong
                api_data = self.fetch_data_from_api(query)
                if api_data:
                    data_fetched.append(api_data.get('quote', ''))
        elif type == "facts":
            if query:
                api_data = self.fetch_data_from_api(query)
                if api_data:
                    data_fetched.append(api_data.get('fact', ''))
            else:
                print(f"{Fore.YELLOW}Untuk 'facts', query diperlukan.{Style.RESET_ALL}")

        if not data_fetched:
            print(f"{Fore.RED}Tidak ada data yang berhasil diambil untuk tipe '{type}'.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.GREEN}Proses scraping selesai. Data siap digunakan.{Style.RESET_ALL}")
        return data_fetched

if __name__ == "__main__":
    scraper = Scraper()
    print("\n--- Testing Local Quotes ---")
    quotes = scraper.update(type="quotes")
    if quotes:
        print(f"Quotes: {quotes[0]}")