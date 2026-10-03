# icebox. — iceqbie.github.io

Portfolio of (ice)^3. Plain HTML/CSS/JS, no build step, served by GitHub Pages from `main`.

## Layout

| Path | What it is |
| --- | --- |
| `/`, `/jp/` | Home (English / Japanese) |
| `/about/`, `/jp/about/` | Profile and skills → Research (interests slider, publications) → Interests → Timeline (research and extracurricular) → CV (education and work, PDF buttons) |
| `/cv/`, `/jp/cv/` | Full CV page; `cv/ice3-cv-en.pdf` and `cv/ice3-cv-ja.pdf` are printed from it |
| `/projects/`, `/jp/projects/` | Project cards |
| `/projects/<slug>/` | Each standalone HTML project |
| `/jp/blog/` | Article cards (the blog is Japanese only; `/blog/` redirects here) |
| `/blog/<slug>/` | Each article |
| `/photos/`, `/jp/photos/` | Unsplash gallery |
| `/data/*.json` | The lists shown on the pages above |
| `tools/import-workbench.py` | Copies the workbench in from `~/self-study` and adds offline support |
| `style.css`, `script.js` | Shared styles; `script.js` fills every `data-list` block from `/data/` |

## Colours

Defined once at the top of `style.css`. Keep to these five (tints of them are fine):

| Colour | HEX | Role | Share |
| --- | --- | --- | ---: |
| White | `#FFFFFF` | base background, whitespace | 65% |
| Light Gray | `#F5F6F7` | section backgrounds, cards | 15% |
| Charcoal | `#252A2E` | text, main UI, icons | 10% |
| Ice Blue | `#A9D9E6` | brand colour, secondary accent | 8% |
| Acid Lime | `#B7F000` | emphasis, hover, special elements | 2% |

Ice Blue and Acid Lime are too light to be text on white — use them as backgrounds, underlines and highlights with Charcoal text on top.

## Typography

Sizes are `rem` tokens (`--fs-*`) at the top of `style.css`, so the visitor's browser font-size setting applies. Nothing is smaller than 13px.

| Role | Face | Weight | Size |
| --- | --- | --- | --- |
| H1 | Inter / Noto Sans JP | 600 | 36–64px (`--fs-h1`) |
| H2 | Inter / Noto Sans JP | 600 | 28–36px (`--fs-h2`) |
| H3, card titles | Inter / Noto Sans JP | 600 | 20px |
| Body | Inter / Noto Sans JP | 400 | 17px, line-height 1.75 (Japanese 1.85) |
| Nav, buttons, links | Inter / Noto Sans JP | 500 | 14–15px |
| Dates, years, tags, badges, numbers | IBM Plex Mono | 400–500 | 13–14px |
| Code | IBM Plex Mono | 400 | 15px |

- The face follows the nearest `lang` attribute: an English title on a Japanese page (`lang="en"`) is set in Inter.
- Use mono only for the metadata in the table, not for buttons or links.
- Don't add letter-spacing to body text or anything Japanese.
- Articles are at most 680px wide (about 40 Japanese characters per line).

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

A project doesn't have to be an HTML page here: `url` can point to a GitHub repo, a PDF or any other page. Leave `thumb` empty (`""`) to get the coloured placeholder.

**Plasma Wave Workbench** — developed in the private `self-study` repo. To update the copy here (it also regenerates the offline cache version):

```sh
cd ~/self-study/basic && python3 tools/build.py --standalone
cd ~/iceqbie.github.io && python3 tools/import-workbench.py
```

Open it once with signal and it keeps working offline; on iPhone, Share → *Add to Home Screen* makes it an app icon.

### Article (Notion → HTML)

Each post is one folder; the originals stay in `blog/_source/`, which git ignores, so nothing private or oversized gets published.

```text
blog/
├── _source/<slug>/          not published: Notion export, original photo and figures
└── <slug>/
    ├── index.html           built by tools/import-notion.py
    ├── thumb.jpg            card and link-preview image (1200px, metadata removed)
    └── figures/fig01-….png
```

1. Write the post in Notion. Where a figure goes, put a line `<>file.png|alt text describing the figure<>`.
2. ••• → Export → HTML. Put the `.html`, the figure files and a thumbnail photo in `blog/_source/<slug>/` (`slug`: lowercase and hyphens, e.g. `astrocamp-2026`).
3. Run:

   ```sh
   python3 tools/import-notion.py "blog/_source/<slug>/<export>.html" \
       --slug <slug> --date 2026-10-03 --thumb "blog/_source/<slug>/<photo>.jpg" \
       --summary "One or two sentences for the card and link previews."
   ```

   It takes the first heading as the title, removes Notion's leftovers (empty paragraphs, stray line breaks, literal `**bold**`, split lists), copies the figures as `figures/fig01-…`, shrinks the photo and strips its EXIF (camera, GPS), and fills in the link-preview tags. Fix any warnings it prints (usually a missing alt text) and run it again.
4. Paste the JSON it prints at the top of `data/articles.json`, and add the English title, English summary and tags.

Re-running the script for the same slug overwrites that post, so edit in Notion and re-export rather than editing `index.html`.

**Publication** — add to the top of `data/publications.json` (`year`, `title`, `journal`, `links`). Home shows the first three. No author lists — see Privacy.

**Timeline and CV** — everything with a date (research experience, talks, awards, activities, qualifications, education, work) lives in `data/timeline.json`; order in the file doesn't matter, every view sorts newest first. The profile timeline shows `research` and `other`; the profile's CV section and the CV pages show `career`; the CV pages and PDFs show everything, by `type`.

```json
{
    "start": "2025-06", "end": "2025-10",
    "kind": "career", "type": "work",
    "title": { "en": "Tenchijin Inc. — Intern", "ja": "株式会社天地人 インターン" },
    "detail": { "en": "", "ja": "" },
    "url": ""
}
```

- `start` / `end`: `"YYYY"` or `"YYYY-MM"`; `end` can be `"present"`; either may be empty (`"start": "", "end": "2023"` shows as 〜2023). The period text (2025年6月–10月 / Jun–Oct 2025) is generated.
- `kind`: `research` (timeline), `other` (timeline, shown as 課外活動 / Extracurricular), `career` (CV only: education and work).
- `type` (badge): `award`, `talk`, `research`, `organizer`, `club`, `volunteer`, `qualification`, `education`, `work`.

**CV PDFs** — `tools/build-cv.sh` prints `/cv/` and `/jp/cv/` to `cv/ice3-cv-en.pdf` and `cv/ice3-cv-ja.pdf` with headless Chrome. You don't need to run it: `.github/workflows/cv.yml` rebuilds and commits both PDFs whenever `data/timeline.json`, `data/publications.json`, the CV pages, `style.css` or `script.js` change. Run it locally only to preview (`tools/build-cv.sh`, then open the PDFs). The CV shows (ice)^3, the affiliation and the site/GitHub links — never a name, phone, email or supervisor.

**Tags** — tags on project and article cards are links: clicking one opens `/projects/?tag=…` or `/jp/blog/?tag=…`, which shows only items with that tag. The bar above each list is built from the tags in the data, so a new tag appears there automatically. Keep spelling identical across items (`AstroCamp`, not `Astrocamp`).

**Photos** — `data/photos.json` is refreshed daily by GitHub Actions (`.github/workflows/unsplash.yml` → `tools/fetch-unsplash.py`) with your most popular Unsplash photos. One-time setup:

1. Create an app at <https://unsplash.com/oauth/applications> (demo mode is enough — one request a day) and copy its **Access Key**.
2. `gh secret set UNSPLASH_ACCESS_KEY` and paste the key (or Settings → Secrets and variables → Actions). The key stays secret; it is never in the site.
3. Actions → *Update Unsplash photos* → *Run workflow* to fill the list now.

Until the key is set, the hand-written list is used as is. Alt text you write in `photos.json` (English or Japanese) is kept on each refresh; a new photo gets Unsplash's English description until you add a Japanese one.

## Previewing locally

The pages load `/data/*.json` with `fetch()` and use root-relative paths, so open them through a local server, not by double-clicking the file.

- **VS Code:** install *Live Server* (ritwickdey.LiveServer), open this folder, right-click `index.html` → *Open with Live Server*. Use the browser's device toolbar to check phone widths.
- **Terminal:** `python3 -m http.server 8000`, then open <http://localhost:8000>.

## Privacy

The real name is intentionally kept off the site. Don't add author lists, a CV PDF, or LinkedIn/Scholar links.
