#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EKDD Materials Downloader

Downloads educational materials (PDFs, DOCs, PPTs, ZIPs) from resources.ekdd.gr.
Organizes files by category and maintains a metadata CSV file.
"""

import os
import re
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

# === Config ===
BASE_URL = "https://resources.ekdd.gr/"
DOWNLOAD_FOLDER = "./data/ekdd_material"
HEADERS = {"User-Agent": "Mozilla/5.0"}

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# === Fetch and parse a webpage ===
def get_soup(url):
    """Fetch and parse HTML from URL."""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


# === Extract category links from the homepage ===
def extract_category_links():
    """Extract category links from the EKDD homepage."""
    soup = get_soup(BASE_URL)
    category_links = []
    
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        
        # Match category URLs and filter by keywords
        if re.search(r"/index\.php/.*", href) and any(
            kw in text for kw in [
                "Διοίκηση", "Οικονομία", "Ανθρώπινα", "Πληροφορική",
                "Βιώσιμη", "Πολιτιστική"
            ]
        ):
            category_links.append((text, urljoin(BASE_URL, href)))
    
    return category_links


# === Extract all subpage links, following pagination ===
def extract_subpages_with_pagination(category_url):
    """Extract all subpage links with pagination support."""
    subpage_links = set()
    page = 0
    step = 10
    
    while True:
        paginated_url = f"{category_url}?start={page}"
        print(f"📄 Crawling page: {paginated_url}")
        
        try:
            soup = get_soup(paginated_url)
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            break
        
        # Extract links on this page
        links_on_page = {
            urljoin(paginated_url, a['href'])
            for a in soup.find_all("a", href=True)
            if "index.php" in a['href'] and not a['href'].endswith(".pdf")
        }
        
        if not links_on_page:
            break
        
        subpage_links.update(links_on_page)
        page += step
    
    return list(subpage_links)


# === Process each category: download files and log metadata ===
def extract_and_download_files(category_name, category_url, csv_writer):
    """Download all files from a category and save metadata."""
    print(f"\n📂 Processing category: {category_name}")
    
    subpage_links = extract_subpages_with_pagination(category_url)
    
    # Create category folder
    category_folder = os.path.join(
        DOWNLOAD_FOLDER,
        re.sub(r"[^\w\s]", "", category_name).strip().replace(" ", "_")
    )
    os.makedirs(category_folder, exist_ok=True)
    
    # Process each subpage
    for subpage_url in tqdm(subpage_links, desc=f"🔍 Searching in {category_name}"):
        try:
            sub_soup = get_soup(subpage_url)
            
            # Extract page title
            title_tag = sub_soup.find("h2") or sub_soup.find("title")
            subpage_title = title_tag.get_text(strip=True) if title_tag else "N/A"
            
            # Find all file links
            file_links = []
            for a in sub_soup.find_all("a", href=True):
                if a['href'].lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.zip')):
                    file_links.append(urljoin(subpage_url, a['href']))
            
            # Download files
            for file_url in file_links:
                filename = file_url.split("/")[-1].split("?")[0]
                filepath = os.path.join(category_folder, filename)
                
                if not os.path.exists(filepath):
                    try:
                        with requests.get(file_url, headers=HEADERS, stream=True, timeout=15) as r:
                            r.raise_for_status()
                            with open(filepath, "wb") as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        print(f"✅ Downloaded: {filename}")
                    except Exception as e:
                        print(f"❌ Error downloading {file_url}: {e}")
                        continue
                else:
                    print(f"⚠️ Already exists: {filename}")
                
                # Save metadata
                csv_writer.writerow([category_name, subpage_title, filename, file_url])
                
        except Exception as e:
            print(f"❌ Failed subpage: {subpage_url}: {e}")


# === MAIN EXECUTION ===
if __name__ == "__main__":
    with open("./data/ekdd_metadata.csv", "w", newline='', encoding="utf-8") as metadata_file:
        csv_writer = csv.writer(metadata_file)
        csv_writer.writerow(["Category", "Subpage Title", "File Name", "File URL"])
        
        categories = extract_category_links()
        
        for name, url in categories:
            extract_and_download_files(name, url, csv_writer)
    
    print("\n✅ All done. Files are in data/ekdd_material/ and metadata is in data/ekdd_metadata.csv.")

