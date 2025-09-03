import os
import io
import time
import random
import zipfile
import requests
from PIL import Image
from playwright.async_api import async_playwright
import shutil
import tempfile
import logging
import asyncio


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# url = ''
min_height = 840
temp_dir = tempfile.mkdtemp()

async def open_page (url):
    async with async_playwright() as p:
        try:
            browser = await p.firefox.launch(headless=False)
            page = await browser.new_page()
            logging.info(f"🌐 Opening page: {url}")
            await page.goto(url, timeout=60000, wait_until="networkidle")

            full_title = await page.title()
            title_split = full_title.split('|')
            title = title_split[1].strip()
            chapter = "".join(char for char in (title_split[0].strip().replace('.', '-')) if char.isdigit() or char == '-')

            # Wait for images that belong to the reader (adjust selector if needed)
            await page.wait_for_selector("img", timeout=30000)

            #forward cookies
            cookies = await page.context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}

            #move mouse randomly
            await page.mouse.move(random.randint(0, 800), random.randint(0, 600))

            # Extract all image src attributes
            image_urls = await page.eval_on_selector_all("img", "els => els.map(e => e.src)")
            await browser.close()

            return title, chapter, cookie_dict, image_urls
        except Exception as e:
            logging.error(f"❌ Failed to open page: {e}")
            raise

async def download_images (url, chapter, cookie_dict, image_urls):
    images = []
    if not image_urls:
        logging.warning("⚠️ No images to download")
        return
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:116.0) Gecko/20100101 Firefox/116.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.140 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.141 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/116.0.5845.140 Mobile Safari/537.36",
    ]

    for idx, img_url in enumerate(image_urls, start=1):
        try:
            # Skip placeholders/branding
            if "brand" in img_url or "logo" in img_url:
                continue

            print(f"[{idx}/{len(image_urls)}] Downloading {img_url}", end="\r", flush=True)
            headers = {
                # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "Referer": url,   # the chapter page URL you opened
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            }

            headers["User-Agent"] = random.choice(user_agents)
            r = requests.get(img_url, headers=headers, cookies=cookie_dict, timeout=20)
            r.raise_for_status()

            img = Image.open(io.BytesIO(r.content))
            width, height = img.size

            if height < min_height:
                print(f"   -> Skipped (height {height}px)")
                continue

            # Save to memory list for CBZ
            filename = f"{int(chapter):04d}-{len(images)+1:03d}.png"
            path = os.path.join(temp_dir, filename)
            img.convert("RGB").save(path, "PNG", quality=100)
            images.append(path)

            # # Sleep randomly to avoid being flagged
            # time.sleep(random.uniform(1.5, 3.5))

        except Exception as e:
            print(f"❌ Error downloading {img_url}: {e}")

    return images

def save_cbz (title, chapter, images):
    if not images:
        logging.warning("⚠️ No valid images to save.")
        return
    
    # Save CBZ
    # Create output directory named after the title
    output_dir = os.path.join(os.getcwd(), "out")
    output_dir = os.path.join(output_dir, title)
    os.makedirs(output_dir, exist_ok=True)

    # Full path for the CBZ file inside that folder
    cbz_name = chapter + '.cbz'
    cbz_path = os.path.join(output_dir, cbz_name)

    with zipfile.ZipFile(cbz_path, "w") as cbz:
        for path in sorted(images):
            cbz.write(path, os.path.basename(path))

    #clear temp directory
    shutil.rmtree(temp_dir)

    logging.info(f"✅ Saved {len(images)} images into {cbz_name}")

    return

def cleanup():
    shutil.rmtree(temp_dir, ignore_errors=True)
    return

async def run(url):
    try:
        title, chapter, cookie_dict, image_urls = await open_page(url)
        images = await download_images(url, chapter, cookie_dict, image_urls)
        return save_cbz(title, chapter, images)
    finally:
        cleanup()

if __name__ == "__main__":
    url = input("Enter page URL: ").strip()
    asyncio.run(run(url))
