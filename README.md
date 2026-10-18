# (ice)^3 — iceqbie.github.io

Portfolio of (ice)^3. Plain HTML/CSS/JS, no build step, served by GitHub Pages from `main`.

## Layout

| Path | What it is |
| --- | --- |
| `/`, `/jp/` | Home (English / Japanese): intro with the panda icon → recent posts and projects (cards, newest first by year) → recent research activities → Unsplash photos |
| `/research/`, `/jp/research/` | Interests, publications, talks and awards, earlier research |
| `/about/`, `/jp/about/` | Short profile: intro, affiliation and field, activities outside research, interests, likes |
| `/projects/`, `/jp/projects/` | Project cards with a tag filter |
| `/projects/<slug>/` | Each standalone HTML project |
| `/jp/blog/` | Article cards with a tag filter (the blog is Japanese only; `/blog/` redirects here) |
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

### Figures and images in posts

Figures, diagrams and generated images use the site's colours arranged by lightness, plus one orange for emphasis. Contrast is against white.

| Step | Colour | HEX | Contrast | Use |
| --- | --- | --- | ---: | --- |
| Background | White | `#FFFFFF` | – | background |
| Panel | Light Gray | `#F5F6F7` | 1.08 | panel ground, always with an outline |
| Pale fill | Pale Ice | `#CBE5EF` | 1.31 | background areas only, always with an outline |
| Fill | Ice Blue | `#A9D9E6` | 1.53 | label grounds; outline it if it carries meaning |
| Visible fill, thick line | Mid Ice | `#4D96B1` | 3.33 | areas that must be told apart, bars |
| Line, arrow, blue text | Deep Ice | `#2F6F8A` | 5.58 | the main data line; blue text |
| Text, outline | Charcoal | `#252A2E` | 14.49 | text and outlines |
| Secondary text | Soft Charcoal | `#5C6268` | 6.17 | on White or Pale Ice only (4.0 on Ice Blue) |
| Emphasis | Signal Orange | `#C2410C` | 5.18 | the one or two things to look at (3.39 on Ice Blue) |

- Pale fills (Light Gray, Pale Ice, Ice Blue) are nearly as light as white, so give them a Charcoal or Deep Ice outline.
- Emphasis is Signal Orange only, once or twice per image. Blue against orange stays distinct for most colour-vision differences.
- Acid Lime is not used in figures: at 1.36 on white it barely shows.
- Size: draw at twice the width the figure is shown at, so it is sharp and its text is readable. Posts are 680px wide, so a PC figure is 1360px wide (for example 1360×720); text is at least 30px in the image (15px on screen), names 34px.
- Phones: a wide figure shrinks to 335px on a phone. Add a narrow version, 670px wide and laid out top to bottom, saved next to the figure as `<name>-mobile.png`; the post shows it below 600px. `tools/import-notion.py` warns when a wide figure has none. Tapping a figure opens it full size.
- Keep figures tight: no empty margins, every name right next to the thing it names.
- The AstroCamp 2026 figure is drawn by `blog/_source/astrocamp-2026/make_fig01.py` (SVG → PNG with `rsvg-convert`; kept on this Mac only, since `blog/_source/` is not in git) and can serve as a starting point.
- Prompt for image generators: *flat, clean illustration on a white background; charcoal #252A2E text and outlines; deep blue #2F6F8A lines; blue #4D96B1 and pale #A9D9E6 / #CBE5EF fills with outlines; one orange #C2410C accent for the key point; no gradients, no shadows.*

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
- Japanese text uses a comma and a period (`, ` and `. `) instead of 、 and 。.
- Articles are at most 680px wide (about 40 Japanese characters per line).

## Adding things

Every list item is written once with `en` and `ja` text, and shows up on Home, the list page, and both languages. Lists are shown in file order — put the newest entry first.

**Project** — put the page at `projects/<slug>/index.html`, then add to `data/projects.json`:

```json
{
    "slug": "my-tool",
    "date": "2026-10",
    "updated": "",
    "title": { "en": "My Tool", "ja": "ツール名" },
    "summary": { "en": "One sentence.", "ja": "一文で説明。" },
    "tags": ["Plasma"],
    "url": "/projects/my-tool/",
    "thumb": "/assets/projects/my-tool.png"
}
```

`date` is when it was published; set `updated` (`"YYYY-MM-DD"`) when you change it, and the card shows both and moves up on Home, which sorts by the later of the two. Articles take the same `updated` field. A project doesn't have to be an HTML page here: `url` can point to a GitHub repo, a PDF or any other page. Leave `thumb` empty (`""`) to get the coloured placeholder.

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
├── _source/<slug>/          not published: the draft (post.md), original photo and figures
└── <slug>/
    ├── index.html           built by tools/import-notion.py
    ├── thumb.jpg            card and link-preview image (1200px, metadata removed)
    └── figures/fig01-….png
```

Drafts are written in Notion: duplicate the page **ブログ下書きテンプレート** (under ブログ in the private hub) and write inside its code block. The draft starts with the post's details, then the body in Markdown:

```text
# Title
slug: astrocamp-2026         URL: /blog/<slug>/
published: 2026-10-03
updated: 2026-10-18          only after a rewrite
caption: One or two sentences for the card and link previews.
tags: AstroCamp, thoughts    spell them like the existing tags
thumbnail: photo.jpg

## First heading
…  **bold**, [link](https://…), > quote, - bullets (nest with 4 spaces)
![alt text describing the figure](figure.png)
```

To publish (or republish after a rewrite):

1. Save the code block's text as `blog/_source/<slug>/post.md`, next to the thumbnail photo and the figure files. (Claude can do this from the Notion link.)
2. Run `python3 tools/import-notion.py blog/_source/<slug>/post.md`. It copies the figures as `figures/fig01-…`, shrinks the photo and strips its EXIF (camera, GPS), fills in the link-preview tags, shows the published and updated dates, and prints the entry for `data/articles.json`. Fix any warnings it prints (usually a missing alt text) and run it again.
3. Put the entry at the top of `data/articles.json` (or update the existing one: title, caption, `updated`), and add the English title and summary.

Re-running the script for the same slug overwrites that post, so edit the draft in Notion rather than editing `index.html`. Older posts exported from Notion as HTML still work: pass the `.html` export with `--slug`, `--date` and `--summary` (see the script's header).

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
- `kind`: `research` (timeline), `other` (timeline, shown as 課外活動 / Extracurricular), `career` (education and work; not shown on the site since the CV was archived).
- `type` (badge): `award`, `talk`, `research`, `organizer`, `club`, `volunteer`, `competition`, `qualification`, `education`, `work`, `internship` (shown in About → Internships).
- `links` (optional): related pages listed under the entry, e.g. event reports — `[{ "label": { "en": "Event report (note)", "ja": "イベントレポート（note）" }, "url": "https://…" }]`. The title's own `url` stays the official page.

**CV** — the CV pages (`/cv/`, `/jp/cv/`), their PDFs, `tools/build-cv.sh` and `.github/workflows/cv.yml` were taken off the site in October 2026. They are kept at the git tag `cv-archive`. To bring them back:

```sh
git checkout cv-archive -- cv/ jp/cv/ tools/build-cv.sh .github/workflows/cv.yml
```

then add `Disallow: /cv/` and `Disallow: /jp/cv/` back to `robots.txt` (the CV carries the real name).

**Tags** — tags on project and article cards are links: clicking one opens `/projects/?tag=…` or `/jp/blog/?tag=…`, which shows only items with that tag. The bar above each list is built from the tags in the data, so a new tag appears there automatically. Keep spelling identical across items (`AstroCamp`, not `Astrocamp`). Give each post or project up to five tags. A post shows its tags under the title (from the draft's `tags:` line), and the Workbench shows its tags in the top bar (from `data/projects.json`, added by `tools/import-workbench.py`).

**Photos** — `data/photos.json` is refreshed daily by GitHub Actions (`.github/workflows/unsplash.yml` → `tools/fetch-unsplash.py`) with your most downloaded Unsplash photos, most downloaded first. One-time setup:

1. Create an app at <https://unsplash.com/oauth/applications> (demo mode is enough — one request a day) and copy its **Access Key**.
2. `gh secret set UNSPLASH_ACCESS_KEY` and paste the key (or Settings → Secrets and variables → Actions). The key stays secret; it is never in the site.
3. Actions → *Update Unsplash photos* → *Run workflow* to fill the list now.

Until the key is set, the hand-written list is used as is. Alt text you write in `photos.json` (English or Japanese) is kept on each refresh; a new photo gets Unsplash's English description until you add a Japanese one.

## Previewing locally

The pages load `/data/*.json` with `fetch()` and use root-relative paths, so open them through a local server, not by double-clicking the file.

- **VS Code:** install *Live Server* (ritwickdey.LiveServer), open this folder, right-click `index.html` → *Open with Live Server*. Use the browser's device toolbar to check phone widths.
- **Terminal:** `python3 -m http.server 8000`, then open <http://localhost:8000>.

## Privacy

The site goes by (ice)^3 and never shows the real name: no author lists, no LinkedIn or Scholar links. The real name only appeared on the CV, which is archived (see CV above).
