import requests
import xml.etree.ElementTree as ET
import hashlib
import os
from datetime import datetime

API_URL = "https://wildix.atlassian.net/wiki/rest/api/content/1256390657?expand=body.storage"
FEED_PATH = "feed.xml"
KEYWORD = "WMS Stable"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})


def generate_rss(items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Wildix WMS Stable Changelog"
    ET.SubElement(channel, "link").text = "https://wildix.atlassian.net/wiki"
    ET.SubElement(channel, "description").text = "Automatischer RSS Feed für WMS Stable Releases"

    for title, content in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "description").text = content
        guid = hashlib.sha256(title.encode()).hexdigest()
        ET.SubElement(item, "guid").text = guid
        ET.SubElement(item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    tree = ET.ElementTree(rss)
    tree.write(FEED_PATH, encoding="utf-8", xml_declaration=True)


# Load Confluence Page
resp = requests.get(API_URL)
json_data = resp.json()
html = json_data["body"]["storage"]["value"]

# Extract headings starting with "WMS Stable"
items = []
for line in html.split("<h2"):
    if KEYWORD in line:
        title_start = line.find(">") + 1
        title_end = line.find("</h2>")
        title = line[title_start:title_end].strip()
        items.append((title, "Neue Version gefunden."))

# Load old feed hash
old_hash = None
if os.path.exists(FEED_PATH):
    with open(FEED_PATH, "rb") as f:
        old_hash = hashlib.sha256(f.read()).hexdigest()

# Generate new feed
generate_rss(items)

# Compare hash to check for new entries
with open(FEED_PATH, "rb") as f:
    new_hash = hashlib.sha256(f.read()).hexdigest()

if old_hash != new_hash:
    if items:
        latest = items[0][0]
        send_telegram(f"Neue Wildix WMS Stable Version entdeckt: {latest}")
