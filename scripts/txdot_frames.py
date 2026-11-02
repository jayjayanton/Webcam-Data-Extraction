"""Discover TxDOT district camera images and optionally download snapshots."""
from __future__ import annotations
import argparse
import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

DISTRICTS = "ABL AMA ATL AUS BMT BWD BRY CHS CRP DAL ELP FTW HOU LRD LBB ODA PAR PHR SJT SAT TYL WAC WFS YKM".split()

def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")[:70] or "camera"

def extract_cameras(html: str, base_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    cameras, seen = [], set()
    for card in soup.select(".card"):
        image = card.select_one("img[src], img[data-src]")
        if image is None:
            continue
        url = urljoin(base_url, image.get("src") or image.get("data-src") or "")
        if urlparse(url).scheme not in ("http", "https") or url in seen:
            continue
        label = card.get_text(" ", strip=True)[:140] or image.get("alt", "") or f"camera-{len(cameras)+1}"
        cameras.append({"camera": label, "image_url": url})
        seen.add(url)
    return cameras

def collect(districts: list[str], outdir: Path, download: bool, headless: bool, wait: float) -> None:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    outdir.mkdir(parents=True, exist_ok=True)
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1500,1000")
    driver = webdriver.Chrome(options=options)
    manifest = []
    try:
        for district in districts:
            page = f"https://its.txdot.gov/its/District/{district}/cameras"
            try:
                driver.get(page)
                time.sleep(wait)
                for _ in range(12):
                    driver.execute_script("window.scrollBy(0, 1200)")
                    time.sleep(0.3)
                records = extract_cameras(driver.page_source, page)
                for n, record in enumerate(records, 1):
                    row = {"district": district, **record, "status": "discovered", "file": ""}
                    if download:
                        try:
                            response = requests.get(record["image_url"], timeout=25, headers={"User-Agent": "Mozilla/5.0"})
                            response.raise_for_status()
                            mime = response.headers.get("content-type", "").lower()
                            if not mime.startswith("image/"):
                                raise ValueError("Response was not an image")
                            ext = ".png" if "png" in mime else ".jpg"
                            target = outdir / district / f'{n:04d}_{safe_name(record["camera"])}{ext}'
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(response.content)
                            row.update(status="downloaded", file=str(target.relative_to(outdir)))
                        except (requests.RequestException, ValueError) as exc:
                            row["status"] = f"error: {exc}"
                    manifest.append(row)
                print(f"{district}: {len(records)} camera images discovered")
            except Exception as exc:
                manifest.append({"district": district, "camera": "", "image_url": page, "status": f"error: {exc}", "file": ""})
    finally:
        driver.quit()
    with (outdir / "camera_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["district", "camera", "image_url", "status", "file"])
        writer.writeheader()
        writer.writerows(manifest)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--districts", nargs="+", default=DISTRICTS)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/txdot"))
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--visible", action="store_true")
    parser.add_argument("--wait", type=float, default=3)
    args = parser.parse_args()
    collect(args.districts, args.output_dir, args.download, not args.visible, args.wait)
