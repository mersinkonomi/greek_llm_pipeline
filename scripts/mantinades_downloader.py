#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mantinades.gr Downloader

Downloads Cretan mantinades (traditional rhyming couplets) from mantinades.gr.
Organizes mantinades by category.
"""

import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

base_url = "https://www.mantinades.gr/"
categories_url = base_url + "mantinades/categories"
output_dir = "./data/mantinades_txt"

os.makedirs(output_dir, exist_ok=True)


def setup_browser():
    """Setup and return a Chrome browser instance."""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment to run headless
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def get_category_links(driver):
    """Extract all category links from the categories page."""
    print("🔍 Fetching categories...")
    driver.get(categories_url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/mantinades/' in href and not href.endswith('categories'):
            full_url = base_url.rstrip('/') + '/' + href.lstrip('/')
            category_name = href.strip('/').split('/')[-1]
            links.append((category_name, full_url))
    
    return links


def extract_mantinades(driver, name, url):
    """Extract all mantinades from a category."""
    print(f"\n🔍 Category: {name}")
    all_mantinades = []
    page = 1
    
    while True:
        full_page_url = url if page == 1 else f"{url}?page={page}"
        driver.get(full_page_url)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "yellow-italic"))
            )
            time.sleep(1)  # Wait for page to load
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            blocks = soup.find_all('div', class_='box-body manti')
            
            if not blocks:
                break
            
            for block in blocks:
                # Extract mantinada text
                mantinada_block = block.find('div', class_='yellow-italic')
                lines = list(mantinada_block.stripped_strings) if mantinada_block else []
                mantinada_text = '\n'.join(lines)
                
                # Extract date
                date_text = ''
                footer = block.find('div', style="border-top: dotted 1px;")
                if footer:
                    date_text = footer.get_text(strip=True)
                
                # Combine into full entry
                if mantinada_text:
                    full_entry = f"{mantinada_text}\n\n{date_text}\n{'-'*40}"
                    all_mantinades.append(full_entry)
            
            print(f" ➕ Page {page}: {len(blocks)} mantinades")
            page += 1
            
        except Exception as e:
            print(f" ⚠️ Error on page {page}: {e}")
            break
    
    # Save to file
    if all_mantinades:
        filepath = os.path.join(output_dir, f"{name}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_mantinades))
        print(f"✅ Saved {len(all_mantinades)} mantinades in category '{name}'")
    else:
        print(f"⚠️ No mantinades found in category '{name}'")


def main():
    """Main execution function."""
    driver = None
    try:
        driver = setup_browser()
        categories = get_category_links(driver)
        
        print(f"✅ Found {len(categories)} categories")
        
        for name, link in categories:
            extract_mantinades(driver, name, link)
            time.sleep(1)  # Be respectful to the server
        
        print("\n🎉 All done!")
        
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()

