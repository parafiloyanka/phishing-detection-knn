import pandas as pd
import requests
import socket
import ssl
import whois
from urllib.parse import urlparse
from datetime import datetime
import time
import random

# Заголовки, щоб прикидатися звичайним браузером (уникаємо блокувань)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


# --- 1. СПИСКИ URL ---

def get_phishing_urls(target_count=80):
    """Завантажує ФІШИНГОВІ посилання (беремо з запасом, бо багато мертвих)"""
    print(f"[STATUS] Завантаження фішингових баз...")
    url = "https://openphish.com/feed.txt"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            urls = list(set(response.text.splitlines()))
            print(f"[OK] Всього знайдено у фіді: {len(urls)} посилань.")
            # Беремо перші 300, щоб після відсіву мертвих залишилось ~80
            return urls[:300]
    except Exception as e:
        print(f"[ERROR] Помилка завантаження фішингу: {e}")
        return []
    return []


def get_benign_urls():
    """Великий список БЕЗПЕЧНИХ сайтів (Топ ресурсів)"""
    return [
        # Пошуковики та Технології
        "google.com", "youtube.com", "facebook.com", "baidu.com", "wikipedia.org",
        "yahoo.com", "reddit.com", "amazon.com", "twitter.com", "instagram.com",
        "linkedin.com", "netflix.com", "microsoft.com", "apple.com", "twitch.tv",
        "stackoverflow.com", "github.com", "bing.com", "wordpress.org", "adobe.com",
        "tumblr.com", "paypal.com", "blogspot.com", "imgur.com", "stackoverflow.com",
        "vk.com", "whatsapp.com", "dropbox.com", "soundcloud.com", "booking.com",
        "bbc.com", "cnn.com", "nytimes.com", "forbes.com", "bloomberg.com",
        # Українські та локальні
        "knu.ua", "monobank.ua", "privat24.ua", "rozetka.com.ua", "olx.ua",
        "ukr.net", "pravda.com.ua", "novaposhta.ua", "diia.gov.ua", "prom.ua",
        # E-commerce & Services
        "ebay.com", "walmart.com", "target.com", "bestbuy.com", "ikea.com",
        "nike.com", "adidas.com", "zara.com", "hm.com", "spotify.com",
        "zoom.us", "salesforce.com", "oracle.com", "ibm.com", "intel.com",
        "amd.com", "nvidia.com", "samsung.com", "sony.com", "lg.com",
        "canon.com", "nikon.com", "tesla.com", "ford.com", "toyota.com",
        "honda.com", "bmw.com", "mercedes-benz.com", "audi.com", "volkswagen.com",
        "metasploit.com", "kali.org", "python.org", "coursera.org", "edx.org"
    ]


# --- 2. АНАЛІЗ АТРИБУТІВ ---

def get_domain_from_url(url):
    try:
        if not url.startswith('http'):
            url = "http://" + url
        parsed = urlparse(url)
        domain = parsed.netloc
        if not domain: domain = parsed.path
        if domain.startswith("www."): domain = domain[4:]
        return domain
    except:
        return None


def get_geolocation_info(domain):
    """Визначає країну за IP (API)"""
    try:
        ip = socket.gethostbyname(domain)
        # Використовуємо ip-api.com
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        return response.get("countryCode", "Unknown")
    except:
        return "Unknown"


def get_whois_features(domain):
    """Whois: Реєстратор та Час життя"""
    features = {"Registrar": "Unknown", "Lifetime": 0}
    try:
        # Тайм-аут для Whois, щоб не висіло вічно
        w = whois.whois(domain)

        if w.registrar:
            reg = w.registrar[0] if isinstance(w.registrar, list) else w.registrar
            features["Registrar"] = str(reg).split(',')[0].strip()

        c_date = w.creation_date
        e_date = w.expiration_date

        if isinstance(c_date, list): c_date = c_date[0]
        if isinstance(e_date, list): e_date = e_date[0]

        if c_date and e_date:
            if isinstance(c_date, datetime) and isinstance(e_date, datetime):
                features["Lifetime"] = (e_date - c_date).days
    except:
        pass
    return features


def get_ssl_info(domain):
    """Перевірка SSL (м'яка, без крашу скрипта)"""
    try:
        ctx = ssl.create_default_context()
        # Ставимо тайм-аут 2 секунди, щоб швидко пропускати "мертві" сайти
        with socket.create_connection((domain, 443), timeout=2) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                return 1  # SSL є
    except:
        return 0  # Немає або помилка з'єднання


# --- 3. ГОЛОВНИЙ ЦИКЛ ОБРОБКИ ---

def process_url(url, label):
    domain = get_domain_from_url(url)
    if not domain: return None

    # Спробуємо резолвити домен. Якщо він мертвий (DNS error), пропускаємо одразу.
    # Це прибере помилки [Errno 8] з консолі
    try:
        socket.gethostbyname(domain)
    except:
        # print(f" -> Пропущено (мертвий домен): {domain}")
        return None

    print(f"Обробка [{label}]: {domain}...")

    features = {
        'URL': url,
        'Class': label,
        'Protocol': 'https' if url.startswith('https') else 'http'
    }

    # Збираємо ознаки
    features['Country'] = get_geolocation_info(domain)
    features.update(get_whois_features(domain))
    features['Has_SSL'] = get_ssl_info(domain)

    return features


if __name__ == "__main__":
    dataset = []
    target_per_class = 75  # Ціль: 75 фішинг + 75 легітимні = 150

    # 1. Списки
    phishing_candidates = get_phishing_urls()
    benign_candidates = get_benign_urls()

    print(f"\nПочинаємо збір даних. Ціль: ~{target_per_class * 2} записів.\n")

    # 2. Обробка ФІШИНГУ
    count = 0
    print("--- Етап 1: Фішингові сайти ---")
    for url in phishing_candidates:
        if count >= target_per_class: break

        # Додаємо http для обробки
        if not url.startswith('http'): url = "http://" + url

        res = process_url(url, "phishing")
        if res:
            dataset.append(res)
            count += 1

    print(f"Зібрано активного фішингу: {count}")

    # 3. Обробка БЕЗПЕЧНИХ
    count = 0
    print("\n--- Етап 2: Безпечні сайти ---")
    for url in benign_candidates:
        if count >= target_per_class: break

        # Додаємо https, бо безпечні сайти зазвичай на ньому
        if not url.startswith('http'): url = "https://" + url

        res = process_url(url, "benign")
        if res:
            dataset.append(res)
            count += 1

    print(f"Зібрано безпечних сайтів: {count}")

    # 4. Збереження
    if len(dataset) > 0:
        df = pd.DataFrame(dataset)

        # Очистка та порядок
        cols = ['URL', 'Registrar', 'Lifetime', 'Country', 'Protocol', 'Has_SSL', 'Class']
        for c in cols:
            if c not in df.columns: df[c] = None
        df = df[cols]

        df.to_csv("train.csv", index=False)
        print("\n" + "=" * 50)
        print(f"[УСПІХ] Файл 'train.csv' створено.")
        print(f"Всього записів: {len(df)}")
        print("=" * 50)
        print(df.head())
    else:
        print("Не вдалося зібрати дані.")