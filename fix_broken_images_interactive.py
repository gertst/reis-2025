import requests
import re
import webbrowser
from PIL import Image
from io import BytesIO

UNSPLASH_ACCESS_KEY = "h0hgH95GF9BtPRTISuUxTCMj1lVlEIKcQlYRMfV0n9o"  # <-- Replace with your Unsplash API key
HTML_PATH = r"c:\\Users\\gerts\\Documents\\Reis 2025\\Reis Tsjechië.html"

# Read HTML
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

# Find all <img ... src="..." alt="..."> tags
img_tags = list(re.finditer(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\']', html))

broken = []

print("Checking images...")
for match in img_tags:
    url, alt = match.group(1), match.group(2)
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            broken.append((match, url, alt))
            continue
        content_type = resp.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            broken.append((match, url, alt))
            continue
        try:
            Image.open(BytesIO(resp.content)).verify()
        except Exception:
            broken.append((match, url, alt))
    except Exception:
        broken.append((match, url, alt))

print(f"\nFound {len(broken)} broken images.")

for idx, (match, url, alt) in enumerate(broken, 1):
    print(f"\n[{idx}/{len(broken)}] Broken image: {url}\n  Alt/search: {alt}")
    # Search Unsplash
    params = {
        "query": alt or "travel",
        "per_page": 3,
        "client_id": UNSPLASH_ACCESS_KEY
    }
    r = requests.get("https://api.unsplash.com/search/photos", params=params)
    results = r.json().get("results", [])
    if not results:
        print("  No Unsplash results found. Skipping.")
        continue
    for i, img in enumerate(results):
        print(f"  Option {i+1}: {img['urls']['regular']}")
        webbrowser.open(img['urls']['regular'])
    choice = input(f"Pick image 1-{len(results)} (or Enter to skip): ").strip()
    if not choice or not choice.isdigit() or not (1 <= int(choice) <= len(results)):
        print("  Skipped.")
        continue
    chosen_url = results[int(choice)-1]['urls']['regular']
    # Replace in HTML
    start, end = match.start(1), match.end(1)
    html = html[:start] + chosen_url + html[end:]
    print(f"  Replaced with: {chosen_url}")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("\nDone! Updated HTML saved.")
