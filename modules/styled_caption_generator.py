# modules/styled_caption_generator.py
import random

def generate_poetic(text):
    templates = [
        f"~{text}~\nSebuah bisikan dari hati.",
        f"{text}.\nKadang diam adalah puisi.",
        f"{text}...\nKetika kata menjadi doa."
    ]
    return random.choice(templates)

def generate_hacker(text):
    templates = [
        f"<{text}>\nSystem override: your destiny.",
        f"{text}\n> Injecting motivation...",
        f"[{text}]\n404: Fear not found."
    ]
    return random.choice(templates)

def generate_lintas(text):
    templates = [
        f"- {text} -\nBerita ini bukan sekadar informasi.",
        f"{text}.\nLintasan pemikiran untuk hari ini.",
        f"- {text} -\nTafsir baru atas kenyataan."
    ]
    return random.choice(templates)

def generate_nalar(text):
    templates = [
        f"\"{text}\"\nLogika terkadang lebih tajam dari rasa.",
        f"{text}.\nMari kita berpikir lebih jauh.",
        f"{text}.\nNalar adalah cahaya di tengah bias."
    ]
    return random.choice(templates)

# Gaya tambahan berdasarkan tema

def generate_asmara(text):
    templates = [
        f"{text}.\nCinta bukan sekadar kata, tapi luka yang indah.",
        f"{text}.\nKadang hati terlalu jujur untuk dipahami.",
        f"{text}...\nAntara rindu dan kecewa, aku tetap menunggu."
    ]
    return random.choice(templates)

def generate_ekonomi(text):
    templates = [
        f"{text}.\nGaji numpang lewat, kebutuhan tetap tinggal.",
        f"{text}.\nDompet tipis, semangat jangan.",
        f"{text}...\nEkonomi melemah, tapi kita harus tetap kuat."
    ]
    return random.choice(templates)

def generate_hangout(text):
    templates = [
        f"{text}!\nKetawa bareng lebih mahal dari apapun.",
        f"{text}...\nKarena waktu bareng teman itu nggak ternilai.",
        f"{text}.\nNgumpul biar waras."
    ]
    return random.choice(templates)

def generate_genz(text):
    templates = [
        f"{text}...\nSkuy dulu baru panik!",
        f"{text}.\nNo drama, just vibe.",
        f"{text}.\nSantuy aja, hidup cuma sekali."
    ]
    return random.choice(templates)

def generate_millenial(text):
    templates = [
        f"{text}...\nPagi ngopi, malam overthinking.",
        f"{text}.\nKerja keras, healing keras juga.",
        f"{text}.\nQuarter life crisis, anyone?"
    ]
    return random.choice(templates)

def generate_kesehatan(text):
    templates = [
        f"{text}.\nSehat itu murah, sakit yang mahal.",
        f"{text}.\nJagalah tubuhmu seperti kamu menjaga chat dia.",
        f"{text}.\nIstirahat bukan lemah, tapi butuh."
    ]
    return random.choice(templates)