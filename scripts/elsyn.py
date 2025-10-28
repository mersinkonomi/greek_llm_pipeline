#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
elsyn.py
----------------------------------
Automated downloader for anonymized decisions from https://www.elsyn.gr/tnp-repo/decisions/search

USAGE:
1️⃣ Run: python elsyn.py
2️⃣ Chrome opens -> Log in via gov.gr (Taxisnet)
3️⃣ After login completes -> press Enter in the terminal
4️⃣ The script opens the results page. Set filters manually and click "Αναζήτηση".
5️⃣ When the table appears -> press Enter again to start automatic downloading.

OPTIONS:
- START_PAGE: where to start (e.g., 1 or 34)
- MAX_PAGES: 0 = all pages, or limit for testing
- Downloads saved in: ./tnp_repo_downloads_click

Requires: pip install selenium webdriver-manager
"""

import json, time, random, platform
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


# ---------------- Settings ----------------
BASE = "https://www.elsyn.gr"
LOGIN_URL = f"{BASE}/tnp-repo/login"
RESULTS_URL = f"{BASE}/tnp-repo/decisions/search"

DOWNLOAD_DIR = Path("data/elsyn_downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

WAIT = 25
DELAY = (0.35, 0.8)
MAX_PAGES = 0        # 0 = all pages
START_PAGE = 34      # 1-based

RESUME_FILE = DOWNLOAD_DIR / "progress.json"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def sleep(): 
    time.sleep(random.uniform(*DELAY))


# ---------------- Driver ----------------
def make_driver():
    opts = Options()
    opts.add_argument("--window-size=1400,1800")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR.resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }
    opts.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_page_load_timeout(60); d.set_script_timeout(60)
    try:
        d.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(DOWNLOAD_DIR.resolve())
        })
    except Exception:
        pass
    return d


# ---------------- Helpers ----------------
def wait_tbody(d, timeout=WAIT):
    return WebDriverWait(d, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "p-table table tbody"))
    )

def wait_refresh(d, old_tbody, timeout=WAIT):
    try:
        WebDriverWait(d, timeout).until(EC.staleness_of(old_tbody))
    except TimeoutException:
        pass
    return wait_tbody(d, timeout)

def next_button(d):
    try:
        btn = d.find_element(By.CSS_SELECTOR, "button.p-paginator-next")
        if "p-disabled" in btn.get_attribute("class") or not btn.is_enabled():
            return None
        return btn
    except Exception:
        return None

def click_safely(d, el):
    try:
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.1)
        ActionChains(d).move_to_element(el).click(el).perform()
        return True
    except Exception:
        try:
            d.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            return False


# ---------------- Resume logic ----------------
def load_progress():
    if RESUME_FILE.exists():
        try:
            return json.loads(RESUME_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_progress(page):
    RESUME_FILE.write_text(json.dumps({"last_page": page}, ensure_ascii=False, indent=2))


# ---------------- Core functions ----------------
def go_to_page(d, page_num, wait=WAIT):
    """Jump to specific 1-based page via paginator input."""
    paginator = WebDriverWait(d, wait).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "p-paginator"))
    )
    inp = paginator.find_element(By.CSS_SELECTOR, "input.p-inputtext")
    d.execute_script("arguments[0].scrollIntoView({block:'center'});", inp)
    time.sleep(0.1)
    inp.click()
    if platform.system() == "Darwin":
        inp.send_keys(Keys.COMMAND, 'a')
    else:
        inp.send_keys(Keys.CONTROL, 'a')
    inp.send_keys(str(page_num))
    try:
        old = d.find_element(By.CSS_SELECTOR, "p-table table tbody")
    except Exception:
        old = None
    inp.send_keys(Keys.ENTER)
    if old: wait_refresh(d, old)
    else:   wait_tbody(d)


def click_all_downloads_on_page(d):
    tbody = wait_tbody(d)
    rows = tbody.find_elements(By.CSS_SELECTOR, "tr")
    if not rows:
        log("No rows on this page.")
        return 0

    clicked = 0
    for i in range(1, len(rows)+1):
        try:
            tbody = d.find_element(By.CSS_SELECTOR, "p-table table tbody")
            row = tbody.find_element(By.CSS_SELECTOR, f"tr:nth-of-type({i})")
        except Exception:
            try:
                tbody = wait_tbody(d)
                row = tbody.find_element(By.CSS_SELECTOR, f"tr:nth-of-type({i})")
            except Exception:
                continue

        btn = None
        try:
            btn = row.find_element(By.XPATH, ".//button[@ptooltip='Μεταφόρτωση Ανωνυμοποιημένου Αρχείου']")
        except Exception:
            try:
                btn = row.find_element(By.XPATH, ".//button[.//span[contains(@class,'pi-download')]]")
            except Exception:
                btn = None

        if not btn:
            continue
        if click_safely(d, btn):
            clicked += 1
            time.sleep(0.25)
        else:
            log(f"⚠️ Couldn't click row {i}.")
        sleep()

    t0 = time.time()
    while time.time() - t0 < 2 and any(DOWNLOAD_DIR.glob("*.crdownload")):
        time.sleep(0.2)
    return clicked


def click_all_pages(d, start_page, max_pages=0):
    total = 0
    current = start_page
    log(f"➡️ Starting from page {current}")

    if current > 1:
        go_to_page(d, current)

    while True:
        clicked = click_all_downloads_on_page(d)
        total += clicked
        log(f"✅ Page {current}: {clicked} files clicked (total: {total})")
        save_progress(current)

        if max_pages and (current - start_page + 1) >= max_pages:
            break
        btn = next_button(d)
        if not btn:
            break
        try:
            old = d.find_element(By.CSS_SELECTOR, "p-table table tbody")
        except Exception:
            old = None
        click_safely(d, btn)
        sleep()
        if old: wait_refresh(d, old)
        else:   wait_tbody(d)
        current += 1

    return total


# ---------------- MAIN ----------------
def main():
    d = make_driver()
    try:
        log("Opening login page…")
        d.get(LOGIN_URL)
        input("👉 Log in via Chrome (gov.gr) and press Enter here… ")

        d.get(RESULTS_URL)
        log("Set filters manually and click 'Αναζήτηση' in Chrome.")
        input("👉 When results appear, press Enter here to start… ")

        wait_tbody(d)

        progress = load_progress()
        start = progress.get("last_page", START_PAGE)
        total = click_all_pages(d, start_page=start, max_pages=MAX_PAGES)

        log(f"\n🎯 Done. Total download buttons clicked: {total}")
        log(f"📂 Files saved in: {DOWNLOAD_DIR.resolve()}")
        log("⚠️ If Chrome asks about multiple downloads, click 'Allow' once.")
    finally:
        try:
            d.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
