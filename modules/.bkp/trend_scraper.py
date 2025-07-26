# modules/trend_scraper.py
import os
import json
import time
from datetime import datetime, timedelta
from colorama import Fore, Style
import requests
from bs4 import BeautifulSoup # Untuk parsing RSS
import traceback
import random

from modules.config import CONFIG

# Impor fungsi gaya caption
try:
    from modules.styled_caption_generator import generate_poetic, generate_hacker, generate_lintas, generate_nalar
except ImportError as e:
    print(f"{Fore.RED}Error: Gagal mengimpor fungsi gaya caption. Pastikan 'styled_caption_generator.py' ada di folder 'modules/' dan fungsi-fungsi tersebut didefinisir: {e}{Style.RESET_ALL}")
    # Berikan fungsi dummy agar script tidak crash jika import gagal
    def generate_poetic(text): return f"~{text}~"
    def generate_hacker(text): return f"<{text}>"
    def generate_lintas(text): return f"- {text} -"
    def generate_nalar(text): return f"\"'{text}\"'"

# Mapping gaya caption
STYLE_FUNCTIONS = {
    "poetic": generate_poetic,
    "hacker": generate_hacker,
    "lintas": generate_lintas,
    "nalar": generate_nalar
}

class TrendScraper:
    def __init__(self):
        self.config = CONFIG
        
        self.cache_file_name = self.config['TREND_CACHE_FILE']
        self.cache_duration_seconds = self.config['TREND_CACHE_DURATION'] * 3600 # Ubah jam ke detik
        self.social_platforms = self.config['SOCIAL_PLATFORMS']
        self.trend_limit = self.config['TREND_LIMIT']
        self.max_api_calls_per_hour = self.config['MAX_API_CALLS_PER_HOUR']
        self.fallback_priority = self.config['FALLBACK_PRIORITY']
        self.trend_txt_path_config = self.config['TREND_TXT'] 
        self.caption_json_path_config = self.config['CAPTION_JSON']
        self.caption_txt_path_config = self.config['CAPTION_TXT']
        self.overlay_dir = self.config['OVERLAY_DIR']
        self.rss_feeds = self.config.get('RSS_FEEDS', [])

        os.makedirs(self.overlay_dir, exist_ok=True)
        
        self.api_calls_made_this_hour = 0
        self.last_api_call_reset_time = datetime.now()

    def _load_cache(self):
        cache_full_path = os.path.join(self.overlay_dir, self.cache_file_name)
        if os.path.exists(cache_full_path):
            try:
                with open(cache_full_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time < timedelta(seconds=self.cache_duration_seconds):
                    print(f"{Fore.GREEN}Menggunakan tren dari cache (diperbarui {cached_time.strftime('%H:%M:%S')}).{Style.RESET_ALL}")
                    return cache_data['trends']
                else:
                    print(f"{Fore.YELLOW}Cache tren kadaluarsa ({self.cache_duration_seconds / 3600:.0f} jam). Mengambil tren baru...{Style.RESET_ALL}")
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"{Fore.YELLOW}Error memuat cache tren ({e}). Mengambil tren baru.{Style.RESET_ALL}")
        return None

    def _save_cache(self, trends):
        cache_full_path = os.path.join(self.overlay_dir, self.cache_file_name)
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'trends': trends
        }
        try:
            with open(cache_full_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"{Fore.GREEN}Tren berhasil disimpan ke cache: {cache_full_path}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error menyimpan cache tren: {e}{Style.RESET_ALL}")

    def _can_make_api_call(self):
        current_time = datetime.now()
        if current_time.hour != self.last_api_call_reset_time.hour:
            self.api_calls_made_this_hour = 0
            self.last_api_call_reset_time = current_time
        
        if self.api_calls_made_this_hour >= self.max_api_calls_per_hour:
            print(f"{Fore.YELLOW}Batas panggilan API ({self.max_api_calls_per_hour}/jam) telah tercapai. Coba lagi nanti.{Style.RESET_ALL}")
            return False
        return True

    def _fetch_trends_from_tiktok(self, limit):
        print(f"{Fore.BLUE}Mencoba mengambil tren dari TikTok... (Placeholder){Style.RESET_ALL}")
        try:
            dummy_tiktok_trends = [
                "Tarian Viral Terbaru", "Challenge TikTok Seru", "Tutorial Gaya Rambut Cepat",
                "Resep Masakan Rumahan", "Trend Fashion Musim Panas", "Tips Produktivitas Hari Ini"
            ]
            return random.sample(dummy_tiktok_trends, min(limit, len(dummy_tiktok_trends)))
        except Exception as e:
            print(f"{Fore.RED}Gagal mengambil tren TikTok: {e}{Style.RESET_ALL}")
            return []

    def _fetch_trends_from_youtube(self, limit):
        print(f"{Fore.BLUE}Mencoba mengambil tren dari YouTube... (Placeholder){Style.RESET_ALL}")
        try:
            dummy_youtube_trends = [
                "Review Gadget Terbaru 2025", "Vlog Traveling Epic", "Musik Populer Bulan Ini",
                "Tutorial Coding Python", "Berita Olahraga Terkini", "Podcast Inspiratif"
            ]
            return random.sample(dummy_youtube_trends, min(limit, len(dummy_youtube_trends)))
        except Exception as e:
            print(f"{Fore.RED}Gagal mengambil tren YouTube: {e}{Style.RESET_ALL}")
            return []
    
    def _fetch_trends_from_rss(self, url, limit):
        print(f"{Fore.CYAN}Mengambil trend dari RSS: {url}{Style.RESET_ALL}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            if "text/html" in response.headers.get("Content-Type", ""):
                print(f"{Fore.RED}✗ Sumber RSS bukan RSS/XML (Content-Type: {response.headers.get('Content-Type', '')}){Style.RESET_ALL}")
                return []

            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")

            if not items:
                print(f"{Fore.YELLOW}⚠️ Tidak ada item <item> ditemukan di {url}{Style.RESET_ALL}")
                return []

            trends = [item.title.text.strip() for item in items if item.title]
            print(f"{Fore.GREEN}✓ {len(trends)} trend ditemukan dari {url}{Style.RESET_ALL}")
            return trends[:limit]

        except requests.RequestException as e:
            print(f"{Fore.RED}✗ Gagal mengakses sumber RSS {url}: {e}{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}✗ Error parsing RSS feed {url}: {e}{Style.RESET_ALL}")
            traceback.print_exc()
            return []

    def read_trend_backup(self):
        trend_txt_full_path = os.path.join(self.overlay_dir, os.path.basename(self.trend_txt_path_config))
        print(f"{Fore.YELLOW}Mencoba menggunakan backup tren lokal dari: {trend_txt_full_path}{Style.RESET_ALL}")
        try:
            with open(trend_txt_full_path, "r", encoding="utf-8") as f:
                trends = [line.strip() for line in f if line.strip()]
            print(f"{Fore.GREEN}✓ {len(trends)} tren dari backup lokal{Style.RESET_ALL}")
            return trends
        except FileNotFoundError:
            print(f"{Fore.RED}✗ File backup tren tidak ditemukan di {trend_txt_full_path}.{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}✗ Error membaca file backup tren: {e}{Style.RESET_ALL}")
            return []

    def get_trends(self, style_name="poetic"):
        print(f"{Fore.CYAN}=== TREND SCRAPER & CAPTION GENERATOR ==={Style.RESET_ALL}")

        trends = []
        
        cached_trends = self._load_cache()
        if cached_trends:
            trends = cached_trends
        
        if not trends:
            print(f"{Fore.CYAN}Mencoba mengambil tren dari sumber online...{Style.RESET_ALL}")
            all_trends_from_sources = []
            
            # Sort platforms based on fallback priority
            prioritized_platforms = sorted(self.social_platforms, 
                                           key=lambda p: self.fallback_priority.index(p) if p in self.fallback_priority else len(self.fallback_priority))

            for platform in prioritized_platforms:
                if not self._can_make_api_call():
                    print(f"{Fore.YELLOW}Melewati {platform} karena batas API tercapai.{Style.RESET_ALL}")
                    break

                current_trends = []
                if platform == 'tiktok':
                    current_trends = self._fetch_trends_from_tiktok(self.trend_limit)
                elif platform == 'youtube':
                    current_trends = self._fetch_trends_from_youtube(self.trend_limit)
                elif platform == 'rss':
                    for rss_url in self.rss_feeds:
                        current_trends.extend(self._fetch_trends_from_rss(rss_url, self.trend_limit))
                        if len(current_trends) >= self.trend_limit:
                            break
                
                if current_trends:
                    all_trends_from_sources.extend(current_trends)
                    self.api_calls_made_this_hour += 1
                    if len(all_trends_from_sources) >= self.trend_limit:
                        break

                time.sleep(1) # Jeda antar panggilan API

            trends = list(dict.fromkeys(all_trends_from_sources)) # Hapus duplikat
            trends = trends[:self.trend_limit]

            if trends:
                self._save_cache(trends)
            else:
                print(f"{Fore.RED}Gagal mengambil tren dari semua sumber online yang dicoba.{Style.RESET_ALL}")
                
        if not trends:
            trends = self.read_trend_backup()

        if not trends:
            print(f"{Fore.RED}✗ Tidak ada tren tersedia sama sekali.{Style.RESET_ALL}")
            return []

        captions = []
        for i, trend in enumerate(trends[:self.trend_limit], 1):
            try:
                styled_text = self.apply_caption_style(trend, style_name)
                captions.append({
                    "id": i,
                    "original_trend": trend,
                    "text": styled_text,
                    "style": style_name
                })
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Gagal proses trend '{trend}' dengan gaya '{style_name}': {e}{Style.RESET_ALL}")
                traceback.print_exc()

        self.save_captions(captions)
        return captions

    def apply_caption_style(self, text, style_name="poetic"):
        func = STYLE_FUNCTIONS.get(style_name, generate_poetic)
        return func(text)

    def save_captions(self, captions):
        caption_json_full_path = os.path.join(self.overlay_dir, os.path.basename(self.caption_json_path_config))
        caption_txt_full_path = os.path.join(self.overlay_dir, os.path.basename(self.caption_txt_path_config))

        try:
            os.makedirs(os.path.dirname(caption_json_full_path), exist_ok=True)

            with open(caption_json_full_path, "w", encoding="utf-8") as f:
                json.dump(captions, f, ensure_ascii=False, indent=2)

            with open(caption_txt_full_path, "w", encoding="utf-8") as f:
                f.write("\n".join([c["text"] for c in captions]))

            print(f"{Fore.GREEN}✓ Caption berhasil disimpan: {len(captions)} entri di {os.path.basename(caption_json_full_path)} dan {os.path.basename(caption_txt_full_path)}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}✗ Gagal menyimpan caption: {e}{Style.RESET_ALL}")
            traceback.print_exc()

# Fungsi alias untuk compatibility dengan main.py
def update(style_name="poetic"):
    scraper = TrendScraper()
    return scraper.get_trends(style_name)

if __name__ == "__main__":
    scraper = TrendScraper()
    print("Mengambil tren dengan gaya 'nalar'...")
    generated_captions = scraper.get_trends(style_name="nalar")
    if generated_captions:
        print(f"\n{Fore.GREEN}Caption yang dihasilkan (pertama):{Style.RESET_ALL}")
        print(generated_captions[0]['text'])
    else:
        print(f"{Fore.RED}Tidak ada caption yang dihasilkan.{Style.RESET_ALL}")