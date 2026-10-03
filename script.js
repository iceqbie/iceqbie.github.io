/* =========================================================
   LIST RENDERER
   Fills every <div data-list="..."> from /data/<name>.json.

     data-list   projects | articles | activities | publications | photos
     data-limit  optional; show only the first N items

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
            link: "Link",
            open: "Open",
            read: "Read",
            written: { en: "English", ja: "Japanese" },
            empty: {
                projects: "Projects will appear here.",
                articles: "Articles are on the way.",
                activities: "Activities will appear here.",
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
            link: "リンク",
            open: "開く",
            read: "読む",
            written: { en: "英語", ja: "日本語" },
            empty: {
                projects: "プロジェクトはここに表示されます。",
                articles: "記事は準備中です。",
                activities: "活動はここに表示されます。",
                publications: "論文はここに表示されます。",
                photos: "写真はここに表示されます。"
            },
            failed: "一覧を読み込めませんでした。ページを再読み込みしてください。"
        }
    }[LANG];


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

    const tagList = (tags) =>
        tags && tags.length
            ? `<ul class="tags" aria-label="Tags">${tags.map((t) => `<li>${escapeHtml(t)}</li>`).join("")}</ul>`
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
                    ${tagList(item.tags)}
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
                    ${tagList(item.tags)}
                </div>
            </article>`;
    }

    function activityRow(item) {
        const title = escapeHtml(pick(item.title));
        const detail = pick(item.detail);
        const heading = item.url
            ? `<a href="${escapeHtml(item.url)}"${linkAttrs(item.url)}>${title}${isExternal(item.url) ? " ↗" : ""}</a>`
            : title;

        return `
            <li class="timeline-item">
                <span class="timeline-year">${escapeHtml(item.year)}</span>
                <div class="timeline-content">
                    <span class="badge badge-${escapeHtml(item.type)}">${escapeHtml(TEXT[item.type] || item.type)}</span>
                    <h3>${heading}</h3>
                    ${detail ? `<p>${escapeHtml(detail)}</p>` : ""}
                </div>
            </li>`;
    }

    // Titles and journals are kept in English on both language pages.
    function publicationRow(item) {
        const links = (item.links || [])
            .map((l) => `<a href="${escapeHtml(l.url)}"${linkAttrs(l.url)}>${escapeHtml(l.label)} ↗</a>`)
            .join("");

        return `
            <li class="publication">
                <span class="publication-year">${escapeHtml(item.year)}</span>
                <div class="publication-body">
                    <h3 lang="en">${escapeHtml(item.title)}</h3>
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
        publications: { item: publicationRow, wrap: (html) => `<ol class="publication-list">${html}</ol>` },
        photos: { item: photoCard, wrap: (html) => html }
    };


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

        try {
            let items = await load(name);
            if (limit > 0) items = items.slice(0, limit);

            container.innerHTML = items.length
                ? renderer.wrap(items.map(renderer.item).join(""))
                : `<p class="list-empty">${escapeHtml(TEXT.empty[name])}</p>`;
        } catch (error) {
            console.error(error);
            container.innerHTML = `<p class="list-empty">${escapeHtml(TEXT.failed)}</p>`;
        }

        container.removeAttribute("aria-busy");
    });

})();
