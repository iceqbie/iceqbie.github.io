"""Turn a Notion draft into a blog post on this site.

From the Markdown draft (the Notion "ブログ下書きテンプレート" format):

    python3 tools/import-notion.py blog/_source/<slug>/post.md

  The draft starts with the title and the post's details, then the body:

    # Title
    slug: astrocamp-2026       (the URL: /blog/<slug>/)
    published: YYYY-MM-DD
    updated: YYYY-MM-DD        (optional)
    caption: One or two sentences for the card and link previews.
    tags: AstroCamp, thoughts  (optional)
    thumbnail: photo.jpg       (next to the draft)

    ## First heading
    …
    ![alt text describing the figure](file.png)

From a Notion HTML export (older posts):

    python3 tools/import-notion.py blog/_source/<slug>/<export>.html \\
        --slug <slug> --date YYYY-MM-DD --thumb blog/_source/<slug>/<photo>.jpg \\
        --summary "One or two sentences for the card and link previews."

Options on the command line win over the details in the draft.

Writes blog/<slug>/index.html, blog/<slug>/thumb.jpg and blog/<slug>/figures/,
then prints the entry to paste into data/articles.json (English title and
summary are left for you to write).

Figures: in a Markdown draft, a line   ![alt text](file.png)   ; in an HTML
export, a line   <>file.png|alt text<>   . Put file.png next to the draft. Figures are copied in order as
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


# ---------------------------------------------------------------- markdown drafts

DETAILS = {"slug", "published", "updated", "caption", "tags", "thumbnail"}


def read_markdown(text):
    """Split a draft into its title, its details (published, caption, …) and the body."""
    title, details, lines = None, {}, text.strip("\n").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        key, sep, value = line.partition(":")
        if not line:
            pass
        elif title is None and line.startswith("# "):
            title = line[2:].strip()
        elif sep and key.strip().lower() in DETAILS:
            details[key.strip().lower()] = value.strip()
        else:
            break
        i += 1
    return title, details, "\n".join(lines[i:])


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2)}"'
                            + (' target="_blank" rel="noopener noreferrer"' if m.group(2).startswith("http") else "")
                            + f">{m.group(1)}</a>", text)
    return text


def markdown_to_html(md):
    """The Markdown a Notion draft uses: headings, paragraphs, bold, links,
    quotes, nested bullet lists and figures. Figures become <>file|alt<>
    markers, which place_figures() then copies in."""
    out, para, items = [], [], []   # items: (depth, text) of the current list

    def flush_para():
        if para:
            out.append(f"<p>{inline(''.join(para))}</p>")
            para.clear()

    def flush_list():
        if not items:
            return
        html_list, depth = "", -1
        for d, text in items:
            if d > depth:
                html_list += "<ul>" * (d - depth)
            else:
                html_list += "</li>" + "</ul></li>" * (depth - d)
            html_list += f"<li>{inline(text)}"
            depth = d
        out.append(html_list + "</li>" + "</ul></li>" * depth + "</ul>")
        items.clear()

    for raw in md.splitlines():
        line = raw.rstrip()
        bullet = re.match(r"^( *)[-*] (.+)$", line)
        image = re.match(r"^!\[(.*?)\]\((.+?)\)$", line.strip())
        heading = re.match(r"^(#{2,4}) (.+)$", line)
        if bullet:
            flush_para()
            items.append((len(bullet.group(1)) // 4, bullet.group(2)))
            continue
        flush_list()
        if not line.strip():
            flush_para()
        elif heading:
            flush_para()
            out.append(f"<h{len(heading.group(1))}>{inline(heading.group(2))}</h{len(heading.group(1))}>")
        elif image:
            flush_para()
            out.append(f"<p>&lt;&gt;{html.escape(image.group(2))}|{html.escape(image.group(1))}&lt;&gt;</p>")
        elif line.startswith(">"):
            flush_para()
            out.append(f"<blockquote><p>{inline(line.lstrip('> ').strip())}</p></blockquote>")
        else:
            para.append(line.strip())
    flush_para()
    flush_list()
    return "\n".join(out)


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

def build_page(title, date, lang, body, summary, slug, has_thumb, updated=""):
    page = TEMPLATE.read_text(encoding="utf8")
    url = f"{SITE}/blog/{slug}/"
    esc = html.escape

    page = page.replace('    <meta name="robots" content="noindex">\n', "")
    page = page.replace("<title>記事タイトル - (ice)^3</title>", f"<title>{esc(title)} - (ice)^3</title>")
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
    label = (lambda word, d: f'<time datetime="{d}">{d}</time> {word}') if lang == "ja" \
        else (lambda word, d: f'{word} <time datetime="{d}">{d}</time>')
    dates = label("公開" if lang == "ja" else "Published", date)
    if updated and updated != date:
        dates += " · " + label("更新" if lang == "ja" else "Updated", updated)
    article = f"""        <article class="prose container" lang="{lang}">

            <p class="prose-meta">
                {dates}
            </p>

            <h1>{esc(title)}</h1>

{body.strip()}

            <a class="back-link" href="{back}">{back_text}</a>

        </article>

"""
    return page[:start] + article + page[end:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", type=pathlib.Path, help="the Markdown draft (.md) or Notion .html export")
    ap.add_argument("--slug", help="URL name, lowercase with hyphens (or slug: in the draft)")
    ap.add_argument("--date", help="publication date, YYYY-MM-DD (or published: in the draft)")
    ap.add_argument("--updated", help="date of the last change, YYYY-MM-DD (or updated: in the draft)")
    ap.add_argument("--lang", default="ja", choices=["ja", "en"])
    ap.add_argument("--thumb", type=pathlib.Path, help="photo for the card and link previews")
    ap.add_argument("--summary", default="", help="one or two sentences for the card and previews")
    args = ap.parse_args()

    export = args.export.read_text(encoding="utf8")
    details, tags = {}, []
    if args.export.suffix.lower() == ".md":
        title, details, markdown = read_markdown(export)
        page_name = title or ""
        body = markdown_to_html(markdown)
        tags = [t.strip() for t in details.get("tags", "").split(",") if t.strip()]
    else:
        page_name = html.unescape(re.search(r"<title>(.*?)</title>", export, re.S).group(1)).strip()
        title, body = take_title(clean(extract_body(export)))

    args.slug = args.slug or details.get("slug")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug or ""):
        sys.exit("import-notion: the slug (--slug or slug:) must be lowercase letters, digits and hyphens")
    args.date = args.date or details.get("published")
    args.updated = args.updated or details.get("updated", "")
    args.summary = args.summary or details.get("caption", "")
    if args.thumb is None and details.get("thumbnail"):
        args.thumb = args.export.parent / details["thumbnail"]
    if args.thumb and not args.thumb.exists():
        sys.exit(f"import-notion: thumbnail {str(args.thumb)!r} not found — put the photo next to the draft")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date or ""):
        sys.exit("import-notion: the publication date (--date or published:) must be YYYY-MM-DD")
    if args.updated and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.updated):
        sys.exit("import-notion: the update date (--updated or updated:) must be YYYY-MM-DD")

    out_dir = REPO / "blog" / args.slug
    if (out_dir / "figures").exists():
        shutil.rmtree(out_dir / "figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    title = title or page_name or args.slug
    body, n_figures = place_figures(body, args.export.parent, out_dir, args.slug)

    kb = None
    if args.thumb:
        kb = make_thumb(args.thumb, out_dir / "thumb.jpg")
    else:
        warn("no --thumb: the card will have no picture and link previews no image")
    if not args.summary:
        warn("no --summary: the card and link previews will have no description")

    (out_dir / "index.html").write_text(
        build_page(title, args.date, args.lang, body, args.summary, args.slug, bool(args.thumb), args.updated),
        encoding="utf8")

    print(f"  wrote blog/{args.slug}/index.html, {n_figures} figure(s)"
          + (f", thumb.jpg ({kb:.0f} KB)" if kb else ""))
    entry = {
        "slug": args.slug, "date": args.date, "updated": args.updated, "lang": args.lang,
        "title": {"en": "", "ja": title} if args.lang == "ja" else {"en": title, "ja": ""},
        "summary": {"en": "", "ja": args.summary} if args.lang == "ja" else {"en": args.summary, "ja": ""},
        "tags": tags,
        "url": f"/blog/{args.slug}/",
        "thumb": f"/blog/{args.slug}/thumb.jpg" if args.thumb else "",
    }
    print("\n  Add to the top of data/articles.json (fill in the other language and tags):\n")
    print(json.dumps(entry, ensure_ascii=False, indent=4))
    if warnings:
        print(f"\n  {len(warnings)} warning(s) — see above.")


if __name__ == "__main__":
    main()
