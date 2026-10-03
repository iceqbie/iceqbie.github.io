/* =========================================================
   LIST RENDERER
   Fills every <div data-list="..."> from /data/<name>.json.

     data-list   projects | articles | activities | career | publications | photos
     data-limit  optional; show only the first N items
     data-kind   activities only: "research" or "other"
     data-filter list pages only: show the tag bar and honour ?tag=
     data-level  heading level for each row (default 3; 4 under an h3)

   Items are written once with { en, ja } fields; the page
   language comes from <html lang>. Lists are shown newest
   first in the order they appear in the JSON file.
   ========================================================= */

(function () {

    const LANG = document.documentElement.lang.startsWith("ja") ? "ja" : "en";

    const TEXT = {
        en: {
            award: "Award",
            talk: "Presentation",
            organizer: "Organizer",
            seminar: "Seminar",
            club: "Extracurricular",
            qualification: "Qualification",
            education: "Education",
            work: "Work",
            written: { en: "English", ja: "Japanese" },
            tags: "Tags",
            all: "All",
            showAll: "Show all",
            matches: (tag, n) => `${n} ${n === 1 ? "item" : "items"} tagged #${tag}`,
            noMatch: (tag) => `Nothing is tagged #${tag}.`,
            empty: {
                projects: "Projects will appear here.",
                articles: "Articles are on the way.",
                activities: "Activities will appear here.",
                career: "Coming soon.",
                publications: "Publications will appear here.",
                photos: "Photos will appear here."
            },
            failed: "Couldn't load this list. Please reload the page."
        },
        ja: {
            award: "受賞",
            talk: "発表",
            organizer: "企画・運営",
            seminar: "ゼミ",
            club: "課外活動",
            qualification: "資格",
            education: "学歴",
            work: "職歴",
            written: { en: "英語", ja: "日本語" },
            tags: "タグ",
            all: "すべて",
            showAll: "すべて表示",
            matches: (tag, n) => `#${tag} の記事・プロジェクト：${n}件`,
            noMatch: (tag) => `#${tag} が付いたものはありません。`,
            empty: {
                projects: "プロジェクトはここに表示されます。",
                articles: "記事は準備中です。",
                activities: "活動はここに表示されます。",
                career: "準備中です。",
                publications: "論文はここに表示されます。",
                photos: "写真はここに表示されます。"
            },
            failed: "一覧を読み込めませんでした。ページを再読み込みしてください。"
        }
    }[LANG];

    // Where a tag on a card leads: the list page, filtered by that tag.
    // The blog exists only in Japanese.
    const LIST_PAGE = {
        projects: LANG === "ja" ? "/jp/projects/" : "/projects/",
        articles: "/jp/blog/"
    };

    // Heading level for list rows; set per container before rendering.
    let LEVEL = 3;

    const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;


    /* ---------- helpers ---------- */

    const escapeHtml = (value) =>
        String(value ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
        }[c]));

    // Pick the current language, falling back to the other one.
    const pick = (field) => {
        if (field == null || typeof field === "string") return field ?? "";
        return field[LANG] || field.en || field.ja || "";
    };

    const isExternal = (url) => /^https?:\/\//.test(url);

    const linkAttrs = (url) =>
        isExternal(url) ? ' target="_blank" rel="noopener noreferrer"' : "";

    const tagHref = (list, tag) => `${LIST_PAGE[list]}?tag=${encodeURIComponent(tag)}`;

    // Tags are links to the filtered list page, like hashtags.
    const tagList = (tags, list) =>
        tags && tags.length
            ? `<ul class="tags" aria-label="${TEXT.tags}">${tags.map((t) => LIST_PAGE[list]
                ? `<li><a class="tag" href="${escapeHtml(tagHref(list, t))}">#${escapeHtml(t)}</a></li>`
                : `<li>${escapeHtml(t)}</li>`).join("")}</ul>`
            : "";


    /* ---------- renderers ---------- */

    function projectCard(item) {
        const title = escapeHtml(pick(item.title));
        const thumb = item.thumb
            ? `<img class="card-thumb" src="${escapeHtml(item.thumb)}" alt="" loading="lazy">`
            : `<div class="card-thumb card-thumb-placeholder" aria-hidden="true"><span>${title.charAt(0)}</span></div>`;

        return `
            <article class="card">
                ${thumb}
                <div class="card-body">
                    <p class="card-meta">${escapeHtml(item.date)}</p>
                    <h3 class="card-title">
                        <a class="card-link" href="${escapeHtml(item.url)}"${linkAttrs(item.url)}>${title}</a>
                    </h3>
                    <p class="card-summary">${escapeHtml(pick(item.summary))}</p>
                    ${tagList(item.tags, "projects")}
                </div>
            </article>`;
    }

    function articleCard(item) {
        const written = TEXT.written[item.lang] || "";
        // The card shows the title in the page language when there is one,
        // so its lang follows what is actually displayed.
        const titleLang = item.title && item.title[LANG] ? LANG : (item.lang || LANG);
        const thumb = item.thumb
            ? `<img class="card-thumb" src="${escapeHtml(item.thumb)}" alt="" loading="lazy">`
            : "";

        return `
            <article class="card">
                ${thumb}
                <div class="card-body">
                    <p class="card-meta">
                        <time datetime="${escapeHtml(item.date)}">${escapeHtml(item.date)}</time>
                        ${written ? `<span class="badge" lang="${escapeHtml(item.lang)}">${escapeHtml(written)}</span>` : ""}
                    </p>
                    <h3 class="card-title" lang="${escapeHtml(titleLang)}">
                        <a class="card-link" href="${escapeHtml(item.url)}"${linkAttrs(item.url)}>${escapeHtml(pick(item.title))}</a>
                    </h3>
                    <p class="card-summary">${escapeHtml(pick(item.summary))}</p>
                    ${tagList(item.tags, "articles")}
                </div>
            </article>`;
    }

    // One row of a CV-style list. `when` may be empty (date not known yet).
    function timelineRow(when, type, item) {
        const title = escapeHtml(pick(item.title));
        const detail = pick(item.detail);
        const heading = item.url
            ? `<a href="${escapeHtml(item.url)}"${linkAttrs(item.url)}>${title}${isExternal(item.url) ? " ↗" : ""}</a>`
            : title;

        return `
            <li class="timeline-item">
                <span class="timeline-year">${escapeHtml(when)}</span>
                <div class="timeline-content">
                    <span class="badge badge-${escapeHtml(type)}">${escapeHtml(TEXT[type] || type)}</span>
                    <h${LEVEL}>${heading}</h${LEVEL}>
                    ${detail ? `<p>${escapeHtml(detail)}</p>` : ""}
                </div>
            </li>`;
    }

    const activityRow = (item) => timelineRow(pick(item.year), item.type, item);
    const careerRow = (item) => timelineRow(pick(item.period), item.type, item);

    // Titles and journals are kept in English on both language pages.
    function publicationRow(item) {
        const links = (item.links || [])
            .map((l) => `<a href="${escapeHtml(l.url)}"${linkAttrs(l.url)}>${escapeHtml(l.label)} ↗</a>`)
            .join("");

        return `
            <li class="publication">
                <span class="publication-year">${escapeHtml(item.year)}</span>
                <div class="publication-body">
                    <h${LEVEL} lang="en">${escapeHtml(item.title)}</h${LEVEL}>
                    <p class="journal" lang="en"><em>${escapeHtml(item.journal)}</em></p>
                    ${links ? `<div class="publication-links">${links}</div>` : ""}
                </div>
            </li>`;
    }

    function photoCard(item) {
        return `
            <a class="photo-card" href="${escapeHtml(item.page)}" target="_blank" rel="noopener noreferrer">
                <img src="${escapeHtml(item.src)}" alt="${escapeHtml(pick(item.alt))}" loading="lazy">
            </a>`;
    }

    const RENDERERS = {
        projects: { item: projectCard, wrap: (html) => `<div class="card-grid">${html}</div>` },
        articles: { item: articleCard, wrap: (html) => `<div class="card-grid">${html}</div>` },
        activities: { item: activityRow, wrap: (html) => `<ol class="timeline">${html}</ol>` },
        career: { item: careerRow, wrap: (html) => `<ol class="timeline">${html}</ol>` },
        publications: { item: publicationRow, wrap: (html) => `<ol class="publication-list">${html}</ol>` },
        photos: { item: photoCard, wrap: (html) => html }
    };


    /* ---------- tag filter (list pages) ---------- */

    // The bar lists every tag with its count; each chip is a plain link
    // to ?tag=…, so a filtered view can be shared and Back works.
    function filterBar(name, all, active) {
        const counts = new Map();
        for (const item of all) for (const t of item.tags || []) counts.set(t, (counts.get(t) || 0) + 1);

        const chip = (href, label, current) =>
            `<li><a class="tag" href="${escapeHtml(href)}"${current ? ' aria-current="true"' : ""}>${label}</a></li>`;

        const chips = [chip(LIST_PAGE[name], escapeHtml(TEXT.all), !active)]
            .concat([...counts].map(([t, n]) =>
                chip(tagHref(name, t), `#${escapeHtml(t)} <span class="tag-count">${n}</span>`, t === active)));

        return `<nav class="tag-filter" aria-label="${TEXT.tags}"><ul class="tags">${chips.join("")}</ul></nav>`;
    }

    function filterStatus(name, active, n) {
        if (!active) return "";
        const text = n ? TEXT.matches(active, n) : TEXT.noMatch(active);
        return `<p class="filter-status" role="status">${escapeHtml(text)}
            <a class="text-link" href="${escapeHtml(LIST_PAGE[name])}">${escapeHtml(TEXT.showAll)}</a></p>`;
    }


    /* ---------- main ---------- */

    const cache = {};

    const load = (name) =>
        cache[name] ??= fetch(`/data/${name}.json`).then((response) => {
            if (!response.ok) throw new Error(`${name}: HTTP ${response.status}`);
            return response.json();
        });

    document.querySelectorAll("[data-list]").forEach(async (container) => {
        const name = container.dataset.list;
        const renderer = RENDERERS[name];
        if (!renderer) return;

        const limit = parseInt(container.dataset.limit, 10);
        const kind = container.dataset.kind;
        const filtering = "filter" in container.dataset && LIST_PAGE[name];
        const active = filtering ? new URLSearchParams(location.search).get("tag") : null;

        try {
            let items = await load(name);
            if (kind) items = items.filter((item) => item.kind === kind);

            const all = items;
            if (active) items = items.filter((item) => (item.tags || []).includes(active));
            if (limit > 0) items = items.slice(0, limit);

            LEVEL = parseInt(container.dataset.level, 10) || 3;
            const list = items.length
                ? renderer.wrap(items.map(renderer.item).join(""))
                : active ? "" : `<p class="list-empty">${escapeHtml(TEXT.empty[name])}</p>`;

            container.innerHTML = filtering
                ? filterBar(name, all, active) + filterStatus(name, active, items.length) + list
                : list;
        } catch (error) {
            console.error(error);
            container.innerHTML = `<p class="list-empty">${escapeHtml(TEXT.failed)}</p>`;
        }

        container.removeAttribute("aria-busy");
    });


    /* ---------- sliders ---------- */

    // A horizontally scrolling row of cards with Previous / Next buttons.
    // Without JavaScript the row still scrolls; the buttons stay hidden.
    document.querySelectorAll("[data-slider]").forEach((slider) => {
        const track = slider.querySelector(".slider-track");
        const controls = slider.querySelector(".slider-controls");
        const [prev, next] = slider.querySelectorAll(".slider-btn");
        const count = slider.querySelector(".slider-count");
        const cards = track.children;

        const step = () => {
            const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
            return cards[0].getBoundingClientRect().width + gap;
        };

        const update = () => {
            const max = track.scrollWidth - track.clientWidth;
            const atEnd = track.scrollLeft >= max - 2;
            const index = atEnd ? cards.length : Math.round(track.scrollLeft / step()) + 1;
            count.textContent = `${index} / ${cards.length}`;
            prev.disabled = track.scrollLeft <= 2;
            next.disabled = atEnd;
            controls.hidden = max <= 2;   // everything fits: no buttons needed
        };

        const go = (dir) => track.scrollBy({ left: dir * step(), behavior: REDUCED_MOTION ? "auto" : "smooth" });

        // Arrow keys scroll the focused track natively; Home / End jump.
        track.addEventListener("keydown", (event) => {
            if (event.key !== "Home" && event.key !== "End") return;
            event.preventDefault();
            track.scrollTo({ left: event.key === "Home" ? 0 : track.scrollWidth, behavior: REDUCED_MOTION ? "auto" : "smooth" });
        });

        prev.addEventListener("click", () => go(-1));
        next.addEventListener("click", () => go(1));
        track.addEventListener("scroll", () => requestAnimationFrame(update), { passive: true });
        window.addEventListener("resize", update);

        controls.hidden = false;
        update();
    });

})();
