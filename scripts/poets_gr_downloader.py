#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Greek Poets Downloader

Downloads poems from poets.gr website.
Organizes poems by poet, with one text file per poet containing all their poems.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Settings
base_url = "https://www.poets.gr"
start_url = base_url + "/el/poihtes"
output_dir = "./data/poets_gr"

os.makedirs(output_dir, exist_ok=True)


def get_soup(url):
    """Fetch and parse HTML from URL."""
    r = requests.get(url)
    r.raise_for_status()
    return BeautifulSoup(r.content, "html.parser")


def extract_poet_links(soup):
    """Extract all poet links from the main page."""
    poets = []
    
    for h3 in soup.select("h3.page-header.item-title"):
        a = h3.find("a")
        if a:
            name = a.text.strip().replace("/", "-")
            link = urljoin(base_url, a["href"])
            poets.append((name, link))
    
    return poets


def extract_poem_links(poet_soup):
    """Extract all poem links for a specific poet."""
    poems = []
    
    for a in poet_soup.select("a.mod-articles-category-title"):
        title = a.get_text(strip=True)
        link = urljoin(base_url, a["href"])
        poems.append((title, link))
    
    return poems


def extract_poem_text(poem_url):
    """Extract poem text from a poem page."""
    soup = get_soup(poem_url)
    body = soup.find("div", itemprop="articleBody")
    
    if not body:
        return ""
    
    # Get all strings, separated by newlines
    lines = list(body.stripped_strings)
    return "\n".join(lines)


# Main execution
if __name__ == "__main__":
    # Step 1: Find all poets (only from main page)
    print("🔍 Connecting to main page...")
    soup = get_soup(start_url)
    poets = extract_poet_links(soup)
    print(f"✅ Found {len(poets)} poets")
    
    # Step 2: For each poet...
    for name, poet_url in poets:
        filepath = os.path.join(output_dir, f"{name}.txt")
        
        if os.path.exists(filepath):
            print(f"⏭️ {name} already exists")
            continue
        
        print(f"\n✍️ Processing {name}")
        
        try:
            poet_soup = get_soup(poet_url)
            poem_links = extract_poem_links(poet_soup)
            
            if not poem_links:
                print("⚠️ No poems found")
                continue
            
            with open(filepath, "w", encoding="utf-8") as f:
                for title, poem_url in poem_links:
                    print(f" 📜 {title}")
                    try:
                        content = extract_poem_text(poem_url)
                        f.write(f"{title}\n{content}\n{'-'*40}\n")
                    except Exception as e:
                        print(f" ❌ Error with poem: {e}")
            
            print(f"✅ Saved {len(poem_links)} poems")
            
        except Exception as e:
            print(f"❌ Error with poet {name}: {e}")
    
    print("\n🎉 Done: All poems saved.")

