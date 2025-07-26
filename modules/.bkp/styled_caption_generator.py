# modules/styled_caption_generator.py
import textwrap
from colorama import Fore, Style, init

init(autoreset=True)

from modules.config import CONFIG

def generate_poetic(text):
    """Menghasilkan caption dengan gaya puitis."""
    wrapped_text = textwrap.fill(text, width=CONFIG['WRAP_WIDTH'])
    return f"~{wrapped_text}~\nSebuah bisikan dari hati."

def generate_hacker(text):
    """Menghasilkan caption dengan gaya hacker."""
    wrapped_text = textwrap.fill(text, width=CONFIG['WRAP_WIDTH'])
    return f"<CODE_INJECTED> // {wrapped_text} // DECRYPTED_MESSAGE"

def generate_lintas(text):
    """Menghasilkan caption dengan gaya berita/lintas."""
    wrapped_text = textwrap.fill(text, width=CONFIG['WRAP_WIDTH'])
    return f"HEADLINE: {wrapped_text.upper()}\n--- Berita Terkini ---"

def generate_nalar(text):
    """Menghasilkan caption dengan gaya analitis/penalaran."""
    wrapped_text = textwrap.fill(text, width=CONFIG['WRAP_WIDTH'])
    return f"// Analisis: {wrapped_text} // Implikasi: [Perlu Dicermati]"

# Fungsi display_captions (opsional, bisa digunakan untuk debugging)
def display_captions(captions_list):
    """Menampilkan caption yang dihasilkan."""
    if not captions_list:
        print(f"{Fore.YELLOW}Tidak ada caption untuk ditampilkan.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}--- Caption yang Dihasilkan ---{Style.RESET_ALL}")
    for caption_data in captions_list:
        print(f"ID: {caption_data.get('id', 'N/A')}")
        print(f"Original: {caption_data.get('original_trend', 'N/A')}")
        print(f"Style: {caption_data.get('style', 'N/A')}")
        print(f"Text:\n{caption_data.get('text', 'N/A')}\n")
    print(f"{Fore.CYAN}------------------------------{Style.RESET_ALL}")