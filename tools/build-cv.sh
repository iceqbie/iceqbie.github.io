#!/usr/bin/env bash
# Print the CV pages (/cv/ and /jp/cv/) to PDF with headless Chrome.
#
#   tools/build-cv.sh            → cv/ice3-cv-en.pdf, cv/ice3-cv-ja.pdf
#
# The pages read data/timeline.json and data/publications.json, so the PDFs
# always match the site. Run by .github/workflows/cv.yml whenever that data
# changes; run it by hand to preview.
set -euo pipefail

cd "$(dirname "$0")/.."

PORT="${CV_PORT:-8765}"
UPDATED="${CV_UPDATED:-$(date +%Y-%m-%d)}"

if [[ -n "${CHROME:-}" ]]; then
    :
elif [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
    CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else
    CHROME="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || true)"
fi
[[ -n "$CHROME" ]] || { echo "build-cv: Chrome not found (set CHROME=…)" >&2; exit 1; }

python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER=$!
PROFILE="$(mktemp -d)"
trap 'kill "$SERVER" 2>/dev/null || true; wait "$SERVER" 2>/dev/null || true; rm -rf "$PROFILE"' EXIT

for _ in $(seq 50); do
    curl -fs "http://127.0.0.1:$PORT/cv/" >/dev/null && break
    sleep 0.2
done

print_pdf() {  # print_pdf <path> <output>
    local out="$2" tmp="$2.tmp"
    rm -f "$tmp"
    "$CHROME" --headless=new --disable-gpu --no-sandbox --no-first-run \
        --user-data-dir="$PROFILE" --no-pdf-header-footer \
        --virtual-time-budget=15000 --run-all-compositor-stages-before-draw \
        --print-to-pdf="$tmp" "http://127.0.0.1:$PORT$1?updated=$UPDATED" >/dev/null 2>&1 &
    local pid=$!
    # Headless Chrome sometimes stays alive after writing the file, so stop
    # it once the PDF is complete (it ends with %%EOF).
    for _ in $(seq 300); do
        if [[ -s "$tmp" ]] && tail -c 64 "$tmp" | grep -q '%%EOF'; then
            kill "$pid" 2>/dev/null || true
            break
        fi
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.2
    done
    wait "$pid" 2>/dev/null || true
    [[ -s "$tmp" ]] || { echo "build-cv: Chrome did not write $out" >&2; exit 1; }
    mv "$tmp" "$out"
    echo "  wrote $out ($(( $(wc -c < "$out") / 1024 )) KB)"
}

print_pdf /cv/ cv/ice3-cv-en.pdf
print_pdf /jp/cv/ cv/ice3-cv-ja.pdf
