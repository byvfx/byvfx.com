#!/usr/bin/env python3
"""Regenerate vfx/index.html from data/credits.json.

Edit the data file, then run this script from the repo root or from anywhere:

    python3 vfx/build.py
"""

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "credits.json"
PAGE = ROOT / "vfx" / "index.html"
IMAGE_DIR = ROOT / "images" / "vfx"
CATEGORIES = ("Film", "TV", "Games", "Commercial")
META_KEYS = ("role", "studio", "year")


def meta_parts(item):
    parts = []
    for key in META_KEYS:
        value = item.get(key, "")
        if not isinstance(value, str):
            value = str(value)
        value = value.strip()
        if value:
            parts.append(value)
    return parts


def load_credits():
    doc = json.loads(DATA.read_text())
    credits = doc.get("credits")
    if not isinstance(credits, list) or not credits:
        raise SystemExit("data/credits.json needs a non-empty credits array")
    for item in credits:
        title = item.get("title", "")
        if not isinstance(title, str) or not title.strip():
            raise SystemExit("every credit needs a title")
        image = item.get("image", "")
        if not isinstance(image, str) or not image.strip() or "/" in image or "\\" in image or ".." in image:
            raise SystemExit(f"{title}: image must be a file name in images/vfx/")
        if not (IMAGE_DIR / image).is_file():
            raise SystemExit(f"{title}: missing images/vfx/{image}")
        category = item.get("category")
        if category not in CATEGORIES:
            raise SystemExit(f"{title}: category must be one of {', '.join(CATEGORIES)}")
        if not isinstance(item.get("selected"), bool):
            raise SystemExit(f"{title}: selected must be true or false")
        for key in META_KEYS:
            if key not in item:
                raise SystemExit(f"{title}: missing {key}")
    return credits


def card_html(item, kind):
    title = html.escape(item["title"])
    image = html.escape(item["image"])
    category = html.escape(item["category"])
    parts = meta_parts(item)
    caption = f'<span class="t">{title}</span>'
    if parts:
        caption += f'<span class="m">{html.escape(" · ".join(parts))}</span>'
    lazy = ' loading="lazy"' if kind == "card" else ""
    return (
        f'<li class="{kind}" data-category="{category}">\n'
        f'          <div class="shot" tabindex="0">\n'
        f'            <span class="thumb"><img src="../images/vfx/{image}" alt=""{lazy}></span>\n'
        f'            <span class="cap">{caption}</span>\n'
        f'          </div>\n'
        f'        </li>'
    )


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VFX | Brandon Young</title>
<meta name="description" content="Brandon Young's VFX credits and CG supervisor reel. Film, television, and game work.">
<meta property="og:title" content="VFX | Brandon Young">
<meta property="og:description" content="Film, television, and game credits, and the CG supervisor reel.">
<meta property="og:image" content="https://byvfx.github.io/images/vfx/westworld.jpg">
<meta property="og:url" content="https://byvfx.github.io/vfx/">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="dark">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23161616'/%3E%3Crect x='6.5' y='6.5' width='19' height='19' fill='none' stroke='%23e3b45f' stroke-width='3' stroke-dasharray='5 3'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #161616;
    --panel: #1e1e1e;
    --line: #333;
    --text: #ececec;
    --muted: #a3a3a3;
    --amber: #E0A040;
    --sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, Consolas, monospace;
    --s1: 4px;
    --s2: 8px;
    --s3: 16px;
    --s4: 24px;
    --s5: 48px;
    --s6: 96px;
    --gutter: var(--s5);
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text); font: 400 17px/1.6 var(--sans); -webkit-font-smoothing: antialiased; }
  img { display: block; max-width: 100%; }
  a { color: inherit; text-decoration-color: #666; text-underline-offset: 3px; }
  a:hover { color: var(--amber); text-decoration-color: var(--amber); }
  a:focus-visible, button:focus-visible { outline: 2px solid var(--amber); outline-offset: 2px; }
  h1, h2, h3, p, ul { margin: 0; padding: 0; }
  ul { list-style: none; }
  button { font: inherit; color: inherit; }

  .wrap { max-width: 1240px; margin: 0 auto; padding: 0 var(--gutter); }
  .mono { font-family: var(--mono); font-size: 13px; letter-spacing: .01em; }
  .muted { color: var(--muted); }

  .top { display: flex; justify-content: space-between; align-items: center; gap: var(--s3); flex-wrap: wrap; padding-top: var(--s4); padding-bottom: var(--s4); }
  .brand { font-weight: 600; text-decoration: none; }
  .top nav { display: flex; align-items: center; gap: var(--s2); }
  .top nav a { text-decoration: none; color: var(--muted); padding: var(--s1) 0; border-bottom: 2px solid transparent; }
  .top nav a:hover { color: var(--amber); }
  .top nav a[aria-current="page"] { color: var(--text); border-bottom-color: var(--amber); }
  .top nav a[aria-current="page"]:hover { color: var(--amber); }
  .top nav .dot { color: #5c5c5c; }

  .hero { margin-top: var(--s3); }
  .hero-line { margin-bottom: var(--s4); }
  .hero-line h1 { font: 400 13px/1.4 var(--mono); color: var(--muted); letter-spacing: .01em; }
  .hero-line h1 b { color: var(--text); font-weight: 500; }

  .window { position: relative; border: 1px dashed #5a5a5a; padding: var(--s3); }
  .coord { position: absolute; font: 400 12px/1 var(--mono); color: var(--amber); background: var(--bg); padding: 0 var(--s2); }
  .coord.size { right: var(--s3); top: -7px; }
  .coord.origin { left: var(--s3); bottom: -6px; }
  .poster { position: relative; aspect-ratio: 16 / 9; background: #0c0c0c; overflow: hidden; }
  .poster img { width: 100%; height: 100%; object-fit: cover; transform: scale(1.03); }
  .poster::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0, 0, 0, 0) 55%, rgba(0, 0, 0, .55)); }
  .poster:focus-within { outline: 2px solid var(--amber); outline-offset: 2px; }
  .play { position: absolute; inset: 0; z-index: 2; width: 100%; height: 100%; margin: 0; padding: 0; border: 0; background: transparent; color: #e6e6e6; cursor: pointer; appearance: none; }
  .play:focus-visible { outline: none; }
  .play-disc { position: absolute; left: 50%; top: 50%; width: 96px; height: 96px; margin: -48px 0 0 -48px; border-radius: 50%; background: rgba(22, 22, 22, .72); border: 1px solid rgba(255, 255, 255, .7); display: grid; place-items: center; }
  .play-disc svg { margin-left: 6px; display: block; }
  .poster .ov { position: absolute; left: var(--s4); right: var(--s4); bottom: var(--s3); display: flex; justify-content: space-between; gap: var(--s3); font: 400 13px/1.4 var(--mono); text-align: left; }
  .poster iframe { position: absolute; inset: 0; z-index: 3; width: 100%; height: 100%; border: 0; background: #000; }

  section { margin-top: var(--s6); }
  .section-head { display: flex; justify-content: space-between; align-items: baseline; gap: var(--s3); padding-bottom: var(--s3); border-bottom: 1px solid var(--line); margin-bottom: var(--s4); }
  .section-head h2 { font-size: 22px; line-height: 1.3; font-weight: 500; letter-spacing: -.01em; }

  .sel { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s5) var(--s4); }
  .credits { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
  .shot { display: block; }
  .shot:focus { outline: none; }
  .thumb { display: block; aspect-ratio: 16 / 9; overflow: hidden; background: #000; border: 1px solid var(--line); }
  .thumb img { width: 100%; height: 100%; object-fit: cover; object-position: center; filter: brightness(.8) saturate(.85); transition: filter .2s; }
  .shot:hover .thumb img,
  .shot:focus-visible .thumb img { filter: none; }
  .shot:focus-visible .thumb { outline: 2px solid var(--amber); outline-offset: 2px; }
  .cap { display: block; margin-top: var(--s2); }
  .feat .cap { margin-top: var(--s3); }
  .feat .t { display: block; font-size: 17px; font-weight: 500; line-height: 1.4; }
  .card { margin-bottom: var(--s3); }
  .card .t { display: block; font: 500 13px/1.4 var(--mono); color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .m { display: block; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .feat .m { font: 400 13px/1.5 var(--mono); margin-top: var(--s1); white-space: normal; }
  .card .m { font: 400 12px/1.5 var(--mono); margin-top: var(--s1); }

  .chips { display: flex; flex-wrap: wrap; gap: var(--s2); margin-bottom: var(--s4); }
  .chip { font: 400 13px/1 var(--mono); color: var(--text); background: transparent; border: 1px solid var(--line); border-radius: 999px; padding: var(--s2) var(--s3); display: inline-flex; gap: var(--s2); align-items: center; cursor: pointer; appearance: none; }
  .chip .n { color: var(--muted); }
  .chip:hover { border-color: #5a5a5a; }
  .chip[aria-pressed="true"],
  .chip[aria-pressed="true"]:hover { border-color: var(--amber); color: var(--amber); }
  .chip[aria-pressed="true"] .n { color: var(--amber); }

  .rows { border-bottom: 1px solid var(--line); }
  .rows li { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 2fr) 56px; gap: var(--s2) var(--s5); align-items: baseline; padding: var(--s3) 0; border-top: 1px solid var(--line); }
  .rows a { font-weight: 500; }
  .rows .mono { text-align: right; }
  .rows .desc { color: #cfcfcf; }
  .contact { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2fr); gap: var(--s3) var(--s5); }
  .contact h2 { font-family: var(--mono); font-weight: 400; font-size: 13px; color: var(--muted); }
  .links { display: flex; flex-wrap: wrap; gap: var(--s2) var(--s4); font-weight: 500; }
  footer.wrap { margin-top: var(--s6); padding-top: var(--s3); padding-bottom: var(--s5); color: var(--muted); }

  @media (max-width: 860px) {
    :root { --gutter: var(--s3); }
    section { margin-top: var(--s5); }
    .hero { margin-top: var(--s2); }
    .window { padding: var(--s2); }
    .play-disc { width: 64px; height: 64px; margin: -32px 0 0 -32px; }
    .play-disc svg { width: 22px; height: 22px; margin-left: 4px; }
    .poster .ov { left: var(--s2); right: var(--s2); bottom: var(--s2); font-size: 12px; }
    .sel { grid-template-columns: minmax(0, 1fr); gap: var(--s4); }
    .credits { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .rows li, .contact { grid-template-columns: minmax(0, 1fr); }
    .rows .mono { text-align: left; }
    .section-head h2 { font-size: 20px; }
    .card .t, .card .m { white-space: normal; }
    .chip { padding: var(--s2) 12px; }
  }
  @media (prefers-reduced-motion: reduce) {
    .thumb img { transition: none; }
  }
</style>
</head>
<body>

<header class="wrap top">
  <a class="brand" href="/">Brandon Young</a>
  <nav class="mono" aria-label="Primary">
    <a href="/#tools">Tools</a><span class="dot" aria-hidden="true">·</span>
    <a href="/vfx/" aria-current="page">VFX</a><span class="dot" aria-hidden="true">·</span>
    <a href="/#about">About</a>
  </nav>
</header>

<main class="wrap">
  <div class="hero">
    <div class="hero-line">
      <h1><b>CG Supervisor</b> · Film, TV &amp; Games</h1>
    </div>
    <div class="window">
      <span class="coord size" aria-hidden="true">1920,1080</span>
      <div class="poster" id="reel">
        <img src="../images/vfx/reel.jpg" alt="">
        <button type="button" class="play" id="reel-play" aria-label="Play Brandon Young FX, CG Supervisor Reel">
          <span class="play-disc" aria-hidden="true"><svg width="32" height="32" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 4l15 8-15 8z" fill="#fff"/></svg></span>
          <span class="ov" aria-hidden="true"><span>Brandon Young FX | CG Supervisor Reel</span><span>2:37</span></span>
        </button>
      </div>
      <span class="coord origin" aria-hidden="true">0,0</span>
    </div>
  </div>

  <section aria-labelledby="sel-h">
    <div class="section-head">
      <h2 id="sel-h">Selected work</h2>
      <span class="mono muted">@@SELECTED_COUNT@@ of @@ALL@@</span>
    </div>
    <ul class="sel">
        @@SELECTED@@
    </ul>
  </section>

  <section id="credits" aria-labelledby="cr-h">
    <div class="section-head">
      <h2 id="cr-h">All credits</h2>
      <span class="mono muted">@@ALL@@ credits</span>
    </div>
    <div class="chips" role="group" aria-label="Filter credits">
      <button type="button" class="chip" data-filter="all" aria-pressed="true">All <span class="n">@@ALL@@</span></button>
      <button type="button" class="chip" data-filter="Film" aria-pressed="false">Film <span class="n">@@FILM@@</span></button>
      <button type="button" class="chip" data-filter="TV" aria-pressed="false">TV <span class="n">@@TV@@</span></button>
      <button type="button" class="chip" data-filter="Games" aria-pressed="false">Games <span class="n">@@GAMES@@</span></button>
    </div>
    <ul class="credits">
        @@GRID@@
    </ul>
  </section>

  <section id="assets" aria-labelledby="as-h">
    <div class="section-head">
      <h2 id="as-h">Assets</h2>
      <a class="mono" href="https://brandonfx.gumroad.com">Gumroad</a>
    </div>
    <ul class="rows">
      <li>
        <a href="https://brandonfx.gumroad.com/l/hymqt">Houdini FLIP Crown Splash</a>
        <span class="desc">A Houdini scene for a crown splash, with two methods for the peaks.</span>
        <span class="mono muted">Scene</span>
      </li>
      <li>
        <a href="https://brandonfx.gumroad.com/l/xxeyI">Vol 1. Modular openVDB Clouds</a>
        <span class="desc">200 modular cloud and fog volumes for applications that read OpenVDB.</span>
        <span class="mono muted">VDB</span>
      </li>
      <li>
        <a href="https://brandonfx.gumroad.com/l/kiGyu">Vol 2. VDB Cumulus Clouds</a>
        <span class="desc">Two sets of 50 cumulus clouds, high resolution and low resolution, with JPG and EXR renders.</span>
        <span class="mono muted">VDB</span>
      </li>
      <li>
        <a href="https://brandonfx.gumroad.com/l/lkeWR">Vol 3. VDB Cirrus Clouds</a>
        <span class="desc">Three sets of 50 cirrus clouds, high resolution and low resolution, with renders.</span>
        <span class="mono muted">VDB</span>
      </li>
    </ul>
  </section>

  <section class="contact" aria-labelledby="ct-h">
    <h2 id="ct-h">Contact</h2>
    <p class="links">
      <a href="mailto:brandon@byvfx.com">brandon@byvfx.com</a>
      <a href="https://github.com/byvfx">GitHub</a>
      <a href="https://www.linkedin.com/in/brandoncyoung">LinkedIn</a>
      <a href="https://vimeo.com/byvfx">Vimeo</a>
    </p>
  </section>
</main>

<footer class="wrap mono">Brandon Young</footer>

<script>
(function () {
  var play = document.getElementById("reel-play");
  var poster = document.getElementById("reel");
  if (play && poster) {
    play.addEventListener("click", function () {
      var frame = document.createElement("iframe");
      frame.src = "https://player.vimeo.com/video/522055702?autoplay=1&title=0&byline=0&portrait=0";
      frame.title = "Brandon Young FX, CG Supervisor Reel";
      frame.setAttribute("allow", "autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share");
      frame.setAttribute("allowfullscreen", "");
      frame.referrerPolicy = "strict-origin-when-cross-origin";
      poster.replaceChildren(frame);
    });
  }

  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var cards = Array.prototype.slice.call(document.querySelectorAll(".credits .card"));
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var filter = chip.getAttribute("data-filter");
      chips.forEach(function (other) {
        other.setAttribute("aria-pressed", other === chip ? "true" : "false");
      });
      cards.forEach(function (card) {
        var show = filter === "all" || card.getAttribute("data-category") === filter;
        card.hidden = !show;
      });
    });
  });
})();
</script>
</body>
</html>
"""


def main():
    credits = load_credits()
    selected = [item for item in credits if item["selected"]]
    rest = [item for item in credits if not item["selected"]]
    counts = {name: sum(1 for item in credits if item["category"] == name) for name in CATEGORIES}
    page = TEMPLATE
    page = page.replace("@@SELECTED@@", "\n        ".join(card_html(item, "feat") for item in selected))
    page = page.replace("@@GRID@@", "\n        ".join(card_html(item, "card") for item in rest))
    page = page.replace("@@SELECTED_COUNT@@", str(len(selected)))
    page = page.replace("@@ALL@@", str(len(credits)))
    page = page.replace("@@FILM@@", str(counts["Film"]))
    page = page.replace("@@TV@@", str(counts["TV"]))
    page = page.replace("@@GAMES@@", str(counts["Games"]))
    if "@@" in page:
        raise SystemExit("unreplaced template token in vfx/index.html")
    if all(not meta_parts(item) for item in credits) and 'class="m"' in page:
        raise SystemExit("role/studio/year are empty but a caption line was rendered")
    for phrase in ("Role · Studio · Year", ">Role<", ">Studio<", ">Year<"):
        if phrase in page:
            raise SystemExit(f"placeholder caption slipped through: {phrase}")
    if "<iframe" in page:
        raise SystemExit("the reel iframe must be created only after the play button is used")
    PAGE.write_text(page)
    print(
        f"wrote {PAGE.relative_to(ROOT)} "
        f"({len(credits)} credits, {len(selected)} selected, "
        f"Film {counts['Film']}, TV {counts['TV']}, Games {counts['Games']}, "
        f"Commercial {counts['Commercial']})"
    )


if __name__ == "__main__":
    sys.exit(main())
