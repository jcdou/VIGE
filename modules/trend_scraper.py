import os
import json
import time
import traceback
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from colorama import Fore, Style
from googleapiclient.discovery import build

from modules.config import CONFIG
from modules.styled_caption_generator import (
    generate_asmara,
    generate_ekonomi,
    generate_hangout,
    generate_genz,
    generate_millenial,
    generate_kesehatan,
    generate_poetic,
    generate_nalar,
    generate_lintas,
    generate_hacker,
)

STYLE_FUNCTIONS = {
    "asmara": generate_asmara,
    "ekonomi": generate_ekonomi,
    "hangout": generate_hangout,
    "genz": generate_genz,
    "millenial": generate_millenial,
    "kesehatan": generate_kesehatan,
    "poetic": generate_poetic,
    "nalar": generate_nalar,
    "lintas": generate_lintas,
    "hacker": generate_hacker,
}

class TrendScraper:
    def __init__(self):
        self.config = CONFIG
        self.overlay_dir = self.config["OVERLAY_DIR"]
        os.makedirs(self.overlay_dir, exist_ok=True)

        self.cache_file_name = self.config["TREND_CACHE_FILE"]
        self.cache_duration_seconds = self.config["TREND_CACHE_DURATION"] * 3600
        self.social_platforms = self.config["SOCIAL_PLATFORMS"]
        self.trend_limit = self.config["TREND_LIMIT"]
        self.max_api_calls_per_hour = self.config["MAX_API_CALLS_PER_HOUR"]
        self.fallback_priority = self.config["FALLBACK_PRIORITY"]
        self.rss_feeds = self.config["RSS_FEEDS"]

        self.trend_txt_path = os.path.join(self.overlay_dir, os.path.basename(self.config["TREND_TXT"]))
        self.caption_json_path = os.path.join(self.overlay_dir, os.path.basename(self.config["CAPTION_JSON"]))
        self.caption_txt_path = os.path.join(self.overlay_dir, os.path.basename(self.config["CAPTION_TXT"]))

        self.api_calls_made_this_hour = 0
        self.last_api_call_reset_time = datetime.now()

    def _can_make_api_call(self):
        now = datetime.now()
        if now.hour != self.last_api_call_reset_time.hour:
            self.api_calls_made_this_hour = 0
            self.last_api_call_reset_time = now
        return self.api_calls_made_this_hour < self.max_api_calls_per_hour

    def _load_cache(self):
        path = os.path.join(self.overlay_dir, self.cache_file_name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cached_time = datetime.fromisoformat(data["timestamp"])
                if datetime.now() - cached_time < timedelta(seconds=self.cache_duration_seconds):
                    print(f"{Fore.GREEN}✓ Menggunakan tren dari cache ({cached_time.strftime('%H:%M:%S')}){Style.RESET_ALL}")
                    return data["trends"]
            except Exception as e:
                print(f"{Fore.YELLOW}Cache tidak valid: {e}{Style.RESET_ALL}")
        return None

    def _save_cache(self, trends):
        path = os.path.join(self.overlay_dir, self.cache_file_name)
        data = {
            "timestamp": datetime.now().isoformat(),
            "trends": trends
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"{Fore.GREEN}✓ Cache tren disimpan.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Gagal menyimpan cache: {e}{Style.RESET_ALL}")

    def _fetch_trends_from_youtube(self, limit):
        print(f"{Fore.BLUE}Ambil tren dari YouTube (REAL)...{Style.RESET_ALL}")
        try:
            api_key = self.config.get("YOUTUBE_API_KEY")
            if not api_key:
                print(f"{Fore.RED}✗ API key YouTube tidak ditemukan dalam config.json{Style.RESET_ALL}")
                return []

            youtube = build("youtube", "v3", developerKey=api_key)
            request = youtube.videos().list(
                part="snippet",
                chart="mostPopular",
                regionCode="ID",
                maxResults=limit
            )
            response = request.execute()
            titles = [item["snippet"]["title"] for item in response.get("items", [])]
            random.shuffle(titles)
            print(f"{Fore.GREEN}✓ {len(titles)} tren YouTube ditemukan.{Style.RESET_ALL}")
            return titles
        except Exception as e:
            print(f"{Fore.RED}✗ Gagal ambil tren YouTube: {e}{Style.RESET_ALL}")
            return []

    def _fetch_trends_from_rss(self, url, limit):
        print(f"{Fore.CYAN}Ambil dari RSS: {url}{Style.RESET_ALL}")
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, "xml")
            items = soup.find_all("item")
            titles = [i.title.text.strip() for i in items if i.title]
            random.shuffle(titles)
            print(f"{Fore.GREEN}✓ {len(titles)} tren ditemukan.{Style.RESET_ALL}")
            return titles[:limit]
        except Exception as e:
            print(f"{Fore.RED}✗ Gagal ambil RSS: {e}{Style.RESET_ALL}")
            return []

    def get_trends(self, style_name="poetic", dynamic_trend_limit=None):
        if style_name not in STYLE_FUNCTIONS and style_name != "mix":
            print(f"{Fore.RED}✗ Gaya '{style_name}' tidak dikenali.{Style.RESET_ALL}")
            return []

        limit = dynamic_trend_limit or self.trend_limit
        print(f"{Fore.CYAN}=== SCRAPE & GENERATE CAPTION ==={Style.RESET_ALL}")
        trends = self._load_cache()

        if not trends:
            all_trends = []
            platforms = sorted(self.social_platforms, key=lambda x: self.fallback_priority.index(x) if x in self.fallback_priority else 99)
            for platform in platforms:
                if not self._can_make_api_call():
                    print(f"{Fore.YELLOW}API limit tercapai, skip {platform}.{Style.RESET_ALL}")
                    break
                current = []
                if platform == "youtube":
                    current = self._fetch_trends_from_youtube(limit)
                elif platform == "rss":
                    for feed in self.rss_feeds:
                        current += self._fetch_trends_from_rss(feed, limit)
                all_trends += current
                self.api_calls_made_this_hour += 1
                time.sleep(1)
            random.shuffle(all_trends)
            trends = list(dict.fromkeys(all_trends))[:limit]
            if trends:
                self._save_cache(trends)

        captions = []
        for i, trend in enumerate(trends[:limit], 1):
            actual_style = style_name if style_name != "mix" else random.choice(list(STYLE_FUNCTIONS.keys()))
            styled = STYLE_FUNCTIONS[actual_style](trend)
            captions.append({"id": i, "original_trend": trend, "text": styled, "style": actual_style})

        with open(self.caption_json_path, "w", encoding="utf-8") as f:
            json.dump(captions, f, ensure_ascii=False, indent=2)
        with open(self.caption_txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(c["text"] for c in captions))
        print(f"{Fore.GREEN}✓ Caption disimpan: {len(captions)} entri.{Style.RESET_ALL}")

        return captions

def update(style_name="poetic", dynamic_trend_limit=None):
    scraper = TrendScraper()
    return scraper.get_trends(style_name, dynamic_trend_limit)
