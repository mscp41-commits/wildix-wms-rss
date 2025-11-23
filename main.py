import os
import requests
from datetime import datetime
import hashlib

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # z. B. -1002100117872
TELEGRAM_THREAD_ID = os.getenv("TELEGRAM_THREAD_ID")  # z. B. 17248

RSS_URL = "https://wildix.atlassian.net/wiki/spaces/DOC/pages/1256390657/WMS+Stable+Changelog+rel70"

STATE_FILE = "last_hash.txt"


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
    }

    if TELEGRAM_THREAD_ID:
        data["message_thread_id"] = int(TELEGRAM_THREAD_ID)

    r = requests.post(url, json=data)

    print("Telegram API response:", r.text)  # <---- WICHTIG


def get_page_content(url):
    """Liest die HTML-Seite und gibt nur den Text für Hashing zurück."""
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def save_hash(value):
    with open(STATE_FILE, "w") as f:
        f.write(value)


def load_hash():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return f.read().strip()


def main():
    print("🔍 Checking for updates...")

    html = get_page_content(RSS_URL)

    # Hash der Seite erzeugen
    current_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()

    last_hash = load_hash()

    if last_hash == current_hash:
        print("No updates found.")
        return

    print("⚠️ New update detected!")
    save_hash(current_hash)

    # Telegram Nachricht senden
    message = f"🚀 *Neues WMS Stable Update entdeckt!*\n\n🔗 {RSS_URL}"
    send_telegram_message(message)

    print("Sent Telegram notification.")


if __name__ == "__main__":
    main()
