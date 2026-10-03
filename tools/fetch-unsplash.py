"""Refresh data/photos.json with the most popular photos on Unsplash.

    UNSPLASH_ACCESS_KEY=… python3 tools/fetch-unsplash.py
    python3 tools/fetch-unsplash.py --from-file response.json   # test without the API

Run daily by .github/workflows/unsplash.yml. The key never reaches the
site: it lives in the repository's Actions secrets. Alt text already
written in photos.json (both languages) is kept for photos that stay in the list;
a new photo falls back to Unsplash's English description until you add
one. If the key is missing or the API fails, the file is left alone.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = REPO / "data" / "photos.json"
USER = "iceqbie"
COUNT = 12
API = f"https://api.unsplash.com/users/{USER}/photos?order_by=popular&per_page={COUNT}"


def fetch(key):
    request = urllib.request.Request(API, headers={
        "Authorization": f"Client-ID {key}",
        "Accept-Version": "v1",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def old_alt(photo, current):
    """Alt text already written for this photo. Page URLs end in the photo id
    (…/photos/<slug>-<id> or …/photos/<id>); ids may contain hyphens."""
    pid = photo["id"]
    for item in current:
        page = item["page"].rstrip("/")
        if page.endswith("/" + pid) or page.endswith("-" + pid):
            return item.get("alt", {})
    return {}


def to_entry(photo, current):
    old = old_alt(photo, current)
    # Alt text written by hand wins; otherwise use Unsplash's description.
    en = old.get("en") or (photo.get("alt_description") or photo.get("description") or "").strip()
    en = en[:1].upper() + en[1:]
    return {
        "page": photo["links"]["html"],
        "src": photo["urls"]["raw"] + "&auto=format&fit=crop&w=1200&q=80",
        "alt": {"en": en, "ja": old.get("ja", "")},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-file", type=pathlib.Path, help="use a saved API response instead of calling Unsplash")
    args = ap.parse_args()

    if args.from_file:
        photos = json.loads(args.from_file.read_text(encoding="utf8"))
    else:
        key = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()
        if not key:
            print("fetch-unsplash: UNSPLASH_ACCESS_KEY is not set — leaving photos.json as it is")
            return
        try:
            photos = fetch(key)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            print(f"fetch-unsplash: Unsplash request failed ({error}) — leaving photos.json as it is", file=sys.stderr)
            return

    if not isinstance(photos, list) or not photos:
        print("fetch-unsplash: no photos in the response — leaving photos.json as it is", file=sys.stderr)
        return

    current = json.loads(PHOTOS.read_text(encoding="utf8")) if PHOTOS.exists() else []
    entries = [to_entry(photo, current) for photo in photos]

    text = json.dumps(entries, ensure_ascii=False, indent=4) + "\n"
    if PHOTOS.exists() and PHOTOS.read_text(encoding="utf8") == text:
        print("fetch-unsplash: no change")
        return
    PHOTOS.write_text(text, encoding="utf8")
    print(f"fetch-unsplash: wrote {len(entries)} photos (most popular first)")


if __name__ == "__main__":
    main()
