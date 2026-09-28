# icebox. — iceqbie.github.io

Portfolio of (ice)^3. Plain HTML/CSS/JS, no build step, served by GitHub Pages from `main`.

## Layout

| Path | What it is |
| --- | --- |
| `/`, `/jp/` | Home (English / Japanese) |
| `/about/`, `/jp/about/` | Profile, interests, publications, activity |
| `/projects/`, `/jp/projects/` | Project cards |
| `/projects/<slug>/` | Each standalone HTML project |
| `/blog/`, `/jp/blog/` | Article cards |
| `/blog/<slug>/` | Each article |
| `/photos/`, `/jp/photos/` | Unsplash gallery |
| `/data/*.json` | The lists shown on the pages above |
| `tools/import-workbench.py` | Copies the workbench in from `~/self-study` and adds offline support |
| `style.css`, `script.js` | Shared styles; `script.js` fills every `data-list` block from `/data/` |

## Adding things

Every list item is written once with `en` and `ja` text, and shows up on Home, the list page, and both languages. Lists are shown in file order — put the newest entry first.

**Project** — put the page at `projects/<slug>/index.html`, then add to `data/projects.json`:

```json
{
    "slug": "my-tool",
    "date": "2026-10",
    "title": { "en": "My Tool", "ja": "ツール名" },
    "summary": { "en": "One sentence.", "ja": "一文で説明。" },
    "tags": ["Plasma"],
    "url": "/projects/my-tool/",
    "thumb": "/assets/projects/my-tool.png"
}
```

Leave `thumb` empty (`""`) to get the coloured placeholder.

**Plasma Wave Workbench** — developed in the private `self-study` repo. To update the copy here (it also regenerates the offline cache version):

```sh
cd ~/self-study/basic && python3 tools/build.py --standalone
cd ~/iceqbie.github.io && python3 tools/import-workbench.py
```

Open it once with signal and it keeps working offline; on iPhone, Share → *Add to Home Screen* makes it an app icon.

### Article (Notion → HTML)

1. Write the draft in Notion, then ••• → Export → HTML, and unzip.
2. Copy `blog/_template.html` to `blog/<slug>/index.html`.
3. Paste everything inside the export's `<div class="page-body">` where the template says `PASTE NOTION CONTENT HERE`. Copy the images into `blog/<slug>/` and fix their `src`.
4. Set the title, date, and `lang` (`ja` or `en`) on `<html>`. Remove the `noindex` line.
5. Add to `data/articles.json`:

```json
{
    "slug": "2026-10-first-post",
    "date": "2026-10-01",
    "lang": "ja",
    "title": { "en": "English title", "ja": "日本語タイトル" },
    "summary": { "en": "", "ja": "要約" },
    "tags": ["Plasma"],
    "url": "/blog/2026-10-first-post/"
}
```

**Activity** — add to the top of `data/activities.json`. `type` is one of `award`, `talk`, `organizer`, `seminar`.

**Photo** — add to `data/photos.json`: the Unsplash photo page URL, the image URL (right-click the photo on Unsplash → copy image address), and alt text in both languages.

## Previewing locally

The pages load `/data/*.json` with `fetch()` and use root-relative paths, so open them through a local server, not by double-clicking the file.

- **VS Code:** install *Live Server* (ritwickdey.LiveServer), open this folder, right-click `index.html` → *Open with Live Server*. Use the browser's device toolbar to check phone widths.
- **Terminal:** `python3 -m http.server 8000`, then open <http://localhost:8000>.

## Privacy

The real name is intentionally kept off the site. Don't add author lists, a CV PDF, or LinkedIn/Scholar links.
