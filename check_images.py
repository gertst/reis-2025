
import requests
from PIL import Image
from io import BytesIO
import re

html_path = r"c:\\Users\\gerts\\Documents\\Reis 2025\\Reis Tsjechië.html"

with open(html_path, encoding="utf-8") as f:
    html = f.read()

# Find all <img ... src="..." alt="..."> tags
img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\']', html)

broken_images = []

for url, alt in img_tags:
    print(f"Checking: {url}")
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"BROKEN (HTTP {resp.status_code})")
            broken_images.append((url, alt))
            continue
        content_type = resp.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"BROKEN (Not an image, got {content_type})")
            broken_images.append((url, alt))
            continue
        try:
            Image.open(BytesIO(resp.content)).verify()
            print("OK")
        except Exception as e:
            print(f"BROKEN (Corrupt image: {e})")
            broken_images.append((url, alt))
    except Exception as e:
        print(f"BROKEN (Exception: {e})")
        broken_images.append((url, alt))

if broken_images:
    print("\nSummary of broken images and suggested search queries:")
    for url, alt in broken_images:
        print(f"BROKEN: {url}\n  Suggested search: {alt if alt else 'No alt text'}")
    print(f"\nTotal broken images: {len(broken_images)}")
else:
    print("\nNo broken images found!")
