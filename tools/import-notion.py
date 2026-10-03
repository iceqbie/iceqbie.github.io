"""Turn a Notion HTML export into a blog post on this site.

    python3 tools/import-notion.py blog/_source/<slug>/<export>.html \\
        --slug <slug> --date YYYY-MM-DD --thumb blog/_source/<slug>/<photo>.jpg \\
        --summary "One or two sentences for the card and link previews."

Writes blog/<slug>/index.html, blog/<slug>/thumb.jpg and blog/<slug>/figures/,
then prints the entry to paste into data/articles.json (English title and
summary are left for you to write).

Figures: in Notion, write a line   <>file.png|alt text<>   where a figure
goes, and put file.png next to the export. Figures are copied in order as
figures/fig01-<name>.png, fig02-…

The thumbnail is shrunk to 1200px (enough for link previews) and its metadata (EXIF: camera, GPS,
date) is removed before it is published. Uses only the standard library
and macOS `sips`.
"""

import argparse
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://iceqbie.github.io"
TEMPLATE = REPO / "blog" / "_template.html"

warnings = []


def warn(msg):
    warnings.append(msg)
    print(f"  warning: {msg}", file=sys.stderr)


def slugify(name):
    name = re.sub(r"^\d+[_-]*", "", name.lower())
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-") or "figure"


# ---------------------------------------------------------------- body cleanup

def extract_body(export):
    m = re.search(r'<div class="page-body">(.*)</div>\s*</article>', export, re.S)
    if not m:
        sys.exit("import-notion: no <div class=\"page-body\"> found — is this a Notion HTML export?")
    return m.group(1)


def clean(body):
    body = re.sub(r'\s(?:id|style|dir|data-notion-[\w-]+)="[^"]*"', "", body)
    body = re.sub(r'\sclass=""', "", body)
    body = re.sub(r'\sdata-notion-callout(?:="")?', "", body)
    body = re.sub(r"<p>\s*</p>", "", body)
    # Notion writes each bullet as its own list; join neighbours into one.
    body = re.sub(r'</ul>\s*<ul class="bulleted-list">', "", body)
    body = re.sub(r'</ol>\s*<ol type="1" class="numbered-list"(?: start="\d+")?>', "", body)
    # A line break inside a paragraph is almost always a stray soft return.
    body = re.sub(r"<br\s*/?>\s*", "", body)
    # Markdown bold that Notion kept as literal asterisks.
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body, flags=re.S)
    while re.search(r"<strong>([^<]*)<strong>(.*?)</strong>([^<]*)</strong>", body):
        body = re.sub(r"<strong>([^<]*)<strong>(.*?)</strong>([^<]*)</strong>",
                      r"<strong>\1</strong>\2<strong>\3</strong>", body)
    body = re.sub(r"<strong></strong>", "", body)
    # External links open in a new tab.
    body = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank" rel="noopener noreferrer">', body)
    return body


def take_title(body):
    m = re.search(r"<h1>(.*?)</h1>", body, re.S)
    if not m:
        warn("no <h1> in the page body — using the Notion page name as the title")
        return None, body
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip(), body[:m.start()] + body[m.end():]


def place_figures(body, source_dir, out_dir, slug):
    figures = out_dir / "figures"
    count = 0

    def figure(m):
        nonlocal count
        spec = html.unescape(m.group(1)).strip()
        name, _, alt = spec.partition("|")
        name, alt = name.strip(), alt.strip()
        src = source_dir / name
        if not src.exists():
            warn(f"figure {name!r} not found next to the export")
            return m.group(0)
        if not alt:
            warn(f"figure {name!r} has no alt text — write <>{name}|description<>")
        count += 1
        dest = f"fig{count:02d}-{slugify(src.stem)}{src.suffix.lower()}"
        figures.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, figures / dest)
        return (f'<figure><img src="/blog/{slug}/figures/{dest}" alt="{html.escape(alt)}" '
                f'loading="lazy"></figure>')

    body = re.sub(r"<p>\s*&lt;&gt;(.+?)&lt;&gt;\s*</p>", figure, body, flags=re.S)
    if "&lt;&gt;" in body:
        warn("a <>…<> figure marker is not on its own line and was left as text")
    return body, count


# ---------------------------------------------------------------- thumbnail

def strip_jpeg_metadata(data):
    """Drop APPn segments except JFIF (APP0) and the ICC profile (APP2)."""
    if data[:2] != b"\xff\xd8":
        sys.exit("import-notion: thumbnail is not a JPEG after conversion")
    out, i = bytearray(b"\xff\xd8"), 2
    while i < len(data):
        if data[i] != 0xFF:
            sys.exit("import-notion: unexpected JPEG structure")
        marker = data[i + 1]
        if marker == 0xDA:  # start of scan: the rest is image data
            out += data[i:]
            break
        length = int.from_bytes(data[i + 2:i + 4], "big")
        segment = data[i:i + 2 + length]
        keep = not (0xE0 <= marker <= 0xEF) or marker == 0xE0 or (
            marker == 0xE2 and segment[4:16] == b"ICC_PROFILE\x00")
        if marker == 0xFE:  # comment
            keep = False
        if keep:
            out += segment
        i += 2 + length
    return bytes(out)


def make_thumb(src, dest):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_jpg = pathlib.Path(tmp) / "thumb.jpg"
        subprocess.run(["sips", "-Z", "1200", "-s", "format", "jpeg", "-s", "formatOptions", "75",
                        str(src), "--out", str(tmp_jpg)], check=True, capture_output=True)
        dest.write_bytes(strip_jpeg_metadata(tmp_jpg.read_bytes()))
    kb = dest.stat().st_size / 1024
    if kb > 300:
        warn(f"thumb.jpg is {kb:.0f} KB — consider a smaller or simpler photo")
    return kb


# ---------------------------------------------------------------- page

def build_page(title, date, lang, body, summary, slug, has_thumb):
    page = TEMPLATE.read_text(encoding="utf8")
    url = f"{SITE}/blog/{slug}/"
    esc = html.escape

    page = page.replace('    <meta name="robots" content="noindex">\n', "")
    page = page.replace("<title>記事タイトル - icebox.</title>", f"<title>{esc(title)} - icebox.</title>")
    page = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{esc(summary)}">', page)
    page = page.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
    page = re.sub(r'<meta property="og:title" content="[^"]*">',
                  f'<meta property="og:title" content="{esc(title)}">', page)
    page = re.sub(r'<meta property="og:description" content="[^"]*">',
                  f'<meta property="og:description" content="{esc(summary)}">', page)
    image = f'\n    <meta property="og:image" content="{SITE}/blog/{slug}/thumb.jpg">' if has_thumb else ""
    page = re.sub(r'<meta property="og:url" content="[^"]*">',
                  f'<meta property="og:url" content="{url}">{image}', page)
    if has_thumb:
        page = page.replace('<meta name="twitter:card" content="summary">',
                            '<meta name="twitter:card" content="summary_large_image">')
    # A post exists in one language, so drop the list-page alternates.
    page = re.sub(r'\n    <link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", page)
    page = page.replace('<link rel="icon"', f'<link rel="canonical" href="{url}">\n\n    <link rel="icon"', 1)

    start = page.index("        <!--\n            HOW TO PUBLISH")
    end = page.index("    </main>")
    back = "/jp/blog/" if lang == "ja" else "/blog/"
    back_text = "← ブログ一覧へ" if lang == "ja" else "← All articles"
    article = f"""        <article class="prose container" lang="{lang}">

            <p class="prose-meta">
                <time datetime="{date}">{date}</time>
            </p>

            <h1>{esc(title)}</h1>

{body.strip()}

            <a class="back-link" href="{back}">{back_text}</a>

        </article>

"""
    return page[:start] + article + page[end:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", type=pathlib.Path, help="the Notion .html export")
    ap.add_argument("--slug", required=True, help="URL name, lowercase with hyphens")
    ap.add_argument("--date", required=True, help="publication date, YYYY-MM-DD")
    ap.add_argument("--lang", default="ja", choices=["ja", "en"])
    ap.add_argument("--thumb", type=pathlib.Path, help="photo for the card and link previews")
    ap.add_argument("--summary", default="", help="one or two sentences for the card and previews")
    args = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        sys.exit("import-notion: --slug must be lowercase letters, digits and hyphens")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        sys.exit("import-notion: --date must be YYYY-MM-DD")

    export = args.export.read_text(encoding="utf8")
    page_name = html.unescape(re.search(r"<title>(.*?)</title>", export, re.S).group(1)).strip()

    out_dir = REPO / "blog" / args.slug
    if (out_dir / "figures").exists():
        shutil.rmtree(out_dir / "figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    body = clean(extract_body(export))
    title, body = take_title(body)
    title = title or page_name
    body, n_figures = place_figures(body, args.export.parent, out_dir, args.slug)

    kb = None
    if args.thumb:
        kb = make_thumb(args.thumb, out_dir / "thumb.jpg")
    else:
        warn("no --thumb: the card will have no picture and link previews no image")
    if not args.summary:
        warn("no --summary: the card and link previews will have no description")

    (out_dir / "index.html").write_text(
        build_page(title, args.date, args.lang, body, args.summary, args.slug, bool(args.thumb)), encoding="utf8")

    print(f"  wrote blog/{args.slug}/index.html, {n_figures} figure(s)"
          + (f", thumb.jpg ({kb:.0f} KB)" if kb else ""))
    entry = {
        "slug": args.slug, "date": args.date, "lang": args.lang,
        "title": {"en": "", "ja": title} if args.lang == "ja" else {"en": title, "ja": ""},
        "summary": {"en": "", "ja": args.summary} if args.lang == "ja" else {"en": args.summary, "ja": ""},
        "tags": [],
        "url": f"/blog/{args.slug}/",
        "thumb": f"/blog/{args.slug}/thumb.jpg" if args.thumb else "",
    }
    print("\n  Add to the top of data/articles.json (fill in the other language and tags):\n")
    print(json.dumps(entry, ensure_ascii=False, indent=4))
    if warnings:
        print(f"\n  {len(warnings)} warning(s) — see above.")


if __name__ == "__main__":
    main()
