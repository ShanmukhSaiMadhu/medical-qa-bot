import requests
from bs4 import BeautifulSoup
import os
import json
import string
import time

BASE_URL = "https://www.mayoclinic.org"
INDEX_TEMPLATE = BASE_URL + "/diseases-conditions/index?letter={}"

def get_valid_links():
    links = []
    for letter in string.ascii_uppercase:
        url = INDEX_TEMPLATE.format(letter)
        print(f"🔄 Scanning: {url}")
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.select("a[href^='/diseases-conditions/']"):
                href = a['href']
                # only include links ending in /symptoms-causes/syc-xxxxx
                if "/symptoms-causes/syc-" in href:
                    full_url = BASE_URL + href
                    if full_url not in links:
                        links.append(full_url)
        except Exception as e:
            print(f"❌ Error loading {url}: {e}")
        time.sleep(0.5)
    return links

def extract_topic(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.find("h1")
        content_div = soup.find("div", class_="content")
        if not title or not content_div:
            return None
        content_text = "\n".join(p.get_text(strip=True) for p in content_div.find_all(["h2", "p", "li"]))
        return {
            "url": url,
            "title": title.get_text(strip=True),
            "content": content_text
        }
    except Exception as e:
        print(f"❌ Error parsing {url}: {e}")
        return None

def main():
    os.makedirs("data", exist_ok=True)
    print("🔍 Gathering valid topic links...")
    topic_links = get_valid_links()
    print(f"✅ Found {len(topic_links)} topics")

    all_topics = []
    for i, link in enumerate(topic_links):
        print(f"📄 [{i+1}/{len(topic_links)}] Fetching {link}")
        topic = extract_topic(link)
        if topic:
            all_topics.append(topic)
        time.sleep(0.5)

    with open("data/mayo_topics.json", "w", encoding="utf-8") as f:
        json.dump(all_topics, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_topics)} topics to data/mayo_topics.json")

if __name__ == "__main__":
    main()
