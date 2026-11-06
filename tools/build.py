#!/usr/bin/env python3
"""
MAVERICK HUB — static site builder.

Reads content/site.json + content/projects.json and writes:
    index.html
    work.html
    about.html
    contact.html
    work/<slug>.html

Run from anywhere:
    python3 tools/build.py

No dependencies. Python 3.9+.
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
PROJECTS = json.loads((ROOT / "content" / "projects.json").read_text(encoding="utf-8"))

YEAR = "2026"
NDA_COUNT = sum(1 for p in PROJECTS if p["client"] == "Under NDA" or p["depth"] == "nda")
CONCEPT_COUNT = sum(1 for p in PROJECTS if p.get("status") == "Concept")
ORIGINAL_COUNT = sum(1 for p in PROJECTS if p.get("status") == "Original")
CLIENT_COUNT = len(PROJECTS) - CONCEPT_COUNT - ORIGINAL_COUNT - NDA_COUNT


def e(value: object) -> str:
    """Escape for text/attribute context."""
    return html.escape(str(value), quote=True)


def url(path: str, base: str = "") -> str:
    return base + path


# ---------------------------------------------------------------- chrome


def head(title: str, desc: str, base: str = "", og_image: str = "") -> str:
    full_title = title if title.startswith(SITE["name"]) else f"{title} — {SITE['name']}"
    canonical = f"{SITE['url']}/{base.replace('../', '')}index.html" if SITE["url"] else ""
    og = ""
    if SITE["url"]:
        image = SITE["url"] + "/assets/img/" + (og_image or PROJECTS[0]["still"]) + ".jpg"
        og = f"""
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(full_title)}">
<meta name="twitter:description" content="{e(desc)}">"""
    canon = f'\n<link rel="canonical" href="{e(canonical)}">' if canonical else ""
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<script>document.documentElement.className = document.documentElement.className.replace('no-js', 'js');</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0B0B0C">
<meta name="color-scheme" content="dark">{canon}{og}
<link rel="icon" href="{url('assets/img/favicon.svg', base)}" type="image/svg+xml">
<link rel="preload" href="{url('assets/fonts/instrument-serif-latin.woff2', base)}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{url('assets/fonts/geist-latin.woff2', base)}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{url('assets/css/main.css', base)}">
</head>
<body>
<div class="grain" aria-hidden="true"></div>
<div class="vignette" aria-hidden="true"></div>
<div class="wipe" aria-hidden="true"></div>
"""


NAV = [
    ("work.html", "01", "Work"),
    ("about.html", "02", "About"),
    ("contact.html", "03", "Contact"),
]


def header(base: str = "", active: str = "") -> str:
    links = []
    for href, num, label in NAV:
        current = ' aria-current="page"' if href == active else ""
        links.append(
            f'<a href="{url(href, base)}"{current}><span class="idx">{num}</span>{label}</a>'
        )
    nav = "\n      ".join(links)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-head" id="head">
  <a class="wordmark" href="{url('index.html', base)}" aria-label="{e(SITE['name'])} — home">Maverick&nbsp;Hub</a>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu">
    <i aria-hidden="true"></i><span>Menu</span>
  </button>
  <nav class="nav" id="nav" aria-label="Primary">
      {nav}
  </nav>
</header>
<main id="main">
"""


def footer(base: str = "") -> str:
    social_links = []
    for s in SITE["social"]:
        rel = ' rel="noopener"' if s["url"] not in ("#", "") else ""
        social_links.append(f'<a href="{e(s["url"])}"{rel}>{e(s["label"])}</a>')
    social = "\n          ".join(social_links)
    return f"""</main>
<footer class="foot wrap">
  <div class="foot__grid">
    <div>
      <p class="wordmark">Maverick&nbsp;Hub</p>
      <p class="kicker" style="margin-top:.8rem">{e(SITE['tagline'])}</p>
    </div>
    <div class="foot__col">
      <span>Index</span>
      <a href="{url('work.html', base)}">Work</a>
      <a href="{url('about.html', base)}">About</a>
      <a href="{url('contact.html', base)}">Contact</a>
    </div>
    <div class="foot__col">
      <span>Elsewhere</span>
          {social}
    </div>
    <div class="foot__col">
      <span>© {YEAR}</span>
      <span>Built frame by frame.</span>
    </div>
  </div>
</footer>
<script src="{url('assets/js/site.js', base)}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- pieces


def project_src(p: dict, base: str = "") -> str:
    return url(f"assets/img/{p['still']}.jpg", base)


def row(p: dict, base: str = "") -> str:
    href = url(f"work/{p['slug']}.html", base)
    client = "Client — NDA" if p["client"] == "Under NDA" else p["client"]
    return f"""  <article class="row" data-reveal>
    <a class="row__media" href="{href}" aria-label="{e(p['title'])} — view project">
      <img src="{project_src(p, base)}" alt="{e(p['title'])} — film still" loading="lazy" width="1600" height="900">
    </a>
    <div class="row__body">
      <span class="row__no kicker">{e(p['no'])} · {e(p['category'])}</span>
      <h3><a href="{href}">{e(p['title'])}</a></h3>
      <p>{e(p['summary'])}</p>
      <div class="row__meta mono"><span>{e(client)}</span><span>·</span><span>{e(p['year'])}</span><span>·</span><span>{e(p['runtime'])}</span></div>
      <a class="row__link" href="{href}">View project <span aria-hidden="true">↗</span></a>
    </div>
  </article>
"""


def stage(no: str, name: str, body: str, specs: list[tuple[str, str]]) -> str:
    rows = "\n".join(
        f'        <li><span>{e(k)}</span><b>{e(v)}</b></li>' for k, v in specs
    )
    return f"""    <div class="stage" data-reveal>
      <span class="stage__no">{e(no)} / {e(name)}</span>
      <h3>{e(name)}</h3>
      <p>{e(body)}</p>
      <ul class="stage__spec">
{rows}
      </ul>
    </div>
"""


def pipeline(base: str = "", show_fig: bool = True) -> str:
    stages = (
        stage(
            "01",
            "Direction",
            "The idea, the script, the look. We lock the frame before anything is generated — references, boards, lens and grade decisions.",
            [("Treatment", "3–6 pages"), ("Lookbook", "Frame-locked"), ("Sign-off", "Before render")],
        )
        + stage(
            "02",
            "Render",
            "Models chosen per shot, not per project. Plates and passes, iterated until the frame behaves like it was lit.",
            [("Passes", "Per shot"), ("Continuity", "Tracked"), ("Review", "Daily cuts")],
        )
        + stage(
            "03",
            "Finish",
            "Edit, sound, colour, delivery. A film, cut like a film — not a folder of clips.",
            [("Sound", "Score & mix"), ("Grade", "Studio LUT"), ("Delivery", "4K + cutdowns")],
        )
    )
    fig = ""
    if show_fig:
        fig = f"""
  <figure class="pipeline__fig">
    <img src="{url('assets/img/process.jpg', base)}" alt="A figure standing over a cracked floor — a frame from Stake Poker" loading="lazy" width="1920" height="1080">
    <figcaption class="mono"><span>Plates and passes</span><span>Iterated per shot — never per project</span></figcaption>
  </figure>"""
    return f"""  <div class="pipeline">
{stages}  </div>{fig}
"""


def credits_dl(p: dict, limit: int = 5) -> str:
    items = p["credits"][:limit]
    return "\n      ".join(
        f"<dt>{e(c['role'])}</dt><dd>{e(c['value'])}</dd>" for c in items
    )


# ---------------------------------------------------------------- pages


def home() -> str:
    three = PROJECTS[:3]
    flagship = PROJECTS[0]
    rail_items = PROJECTS[3:]

    rows = "\n".join(row(p) for p in three)
    rail = "\n".join(
        f"""    <figure>
      <a href="work/{p['slug']}.html" data-no-wipe>
        <img src="assets/img/{p['still']}.jpg" alt="{e(p['title'])} — still from the film" loading="lazy" width="1600" height="900">
      </a>
      <figcaption><b>{e(p['title'])}</b><span>{e(p['category'])}</span></figcaption>
    </figure>"""
        for p in rail_items
    )

    doc = (
        head(
            f"{SITE['name']} — AI film studio for brands",
            SITE["description"],
            og_image=PROJECTS[0]["still"],
        )
        + header()
        + f"""
<section class="hero" aria-label="Introduction">
  <div class="hero__media">
    <img src="assets/img/hero.jpg" alt="A space station against a star field — a frame from Watchers" fetchpriority="high" width="1920" height="1080">
  </div>
  <div class="hero__top wrap">
    <p class="kicker"><span class="kicker--crimson">●</span>&nbsp; {e(SITE['availability'])}</p>
    <p class="kicker">Independent studio · {YEAR}</p>
  </div>
  <div class="hero__inner wrap">
    <h1>Every frame<br>is a <em>decision.</em></h1>
    <p class="hero__sub">A film studio for brands. Directed and cut by hand — rendered without a crew.</p>
    <div class="hero__foot">
      <div class="hero__actions">
        <a class="btn" href="contact.html">Start a project <span aria-hidden="true">→</span></a>
        <a class="btn btn--ghost" href="work.html">See the work <span aria-hidden="true">↘</span></a>
      </div>
      <div class="transport" aria-hidden="true">
        <span class="transport__play"></span>
        <span class="transport__bar"><i></i></span>
        <span>00:00:23</span>
      </div>
    </div>
  </div>
</section>

<section class="act wrap" id="work">
  <div class="act__head">
    <p class="kicker">Selected work</p>
    <p class="count"><a class="count--link" href="work.html">01 — 03 / {len(PROJECTS):02d} &nbsp;↗</a></p>
  </div>
{rows}</section>

<section class="manifesto" aria-label="Method">
  <div class="wrap">
    <div class="manifesto__inner" data-reveal>
      <p class="kicker">Note 003 — Method</p>
      <blockquote>
        We don't render a prompt.<br>
        We <em>direct</em> a film — cast the light,
        choose the lens, hold the cut,
        and throw away <span class="hot">the take</span> that
        <span class="d">almost</span> <span class="d">worked.</span>
      </blockquote>
      <p class="kicker manifesto__sig">Maverick Hub — a one-room studio</p>
    </div>
  </div>
</section>

<section class="act wrap" aria-label="How it is made">
  <div class="act__head">
    <p class="kicker">How it's made</p>
    <p class="count">Three stages, every time</p>
  </div>
{pipeline()}</section>

<section class="flagship" aria-label="Flagship study">
  <img src="assets/img/{flagship['still']}.jpg" alt="{e(flagship['title'])} — flagship film still" loading="lazy" width="1600" height="900">
  <div class="flagship__inner wrap">
    <div>
      <p class="kicker">Flagship study · {e(flagship['runtime'])}</p>
      <h2>{e(flagship['title'])}</h2>
      <div class="flagship__cta">
        <span class="transport__play" aria-hidden="true"></span>
        <a class="row__link" href="work/{flagship['slug']}.html">Open the study <span aria-hidden="true">↗</span></a>
      </div>
    </div>
    <dl class="credits">
      {credits_dl(flagship)}
    </dl>
  </div>
</section>

<section class="act wrap" aria-label="Range">
  <div class="act__head">
    <p class="kicker">Range — {len(rail_items):02d} films</p>
    <p class="count"><a class="count--link" href="work.html">Full index ↗</a></p>
  </div>
  <div class="rail" tabindex="0" role="region" aria-label="More films, horizontally scrollable">
{rail}
  </div>
  <div class="rail__prog" aria-hidden="true"><i></i></div>
  <p class="kicker rail__note">{CLIENT_COUNT} client films · {CONCEPT_COUNT} concepts · {ORIGINAL_COUNT} originals — labelled, never blurred.</p>
</section>

<section class="act wrap" id="studio">
  <div class="studio" data-reveal>
    <div class="studio__img">
      <img src="assets/img/portrait.jpg" alt="{e(SITE['founder'])}, founder and director" loading="lazy" width="1100" height="1375">
    </div>
    <div class="studio__body">
      <p class="kicker">The studio</p>
      <h2>A one-room studio, on purpose.</h2>
      <p>Maverick Hub is a small studio that works on a handful of films at a time. I direct and cut AI-made films for brands that need volume without losing taste.</p>
      <p>AI production is the method, not the pitch — the work should stand up as film first, and as a new way of making it second.</p>
      <div class="studio__sig">
        <b>{e(SITE['founder'])}</b>
        <span class="kicker">Founder, director</span>
        <span class="kicker" style="color:var(--ash-dim)">{('Based ' + e(SITE['city']) + ' · ') if SITE.get('city') else ''}{e(SITE['hours'])}</span>
      </div>
    </div>
  </div>
</section>

<section class="close" aria-label="Start a project">
  <div class="wrap close__inner">
    <h2>The next frame<br>is <em>yours.</em></h2>
    <a class="btn" href="contact.html">Start a project <span aria-hidden="true">→</span></a>
    <span class="close__mail">{e(SITE['email'])}</span>
  </div>
</section>
"""
        + footer()
    )
    return doc


def work_index() -> str:
    categories = ["All"] + sorted({p["category"] for p in PROJECTS})
    filters = "\n      ".join(
        f'<button class="filter" type="button" data-filter="{e(c)}" aria-pressed="{"true" if c == "All" else "false"}">{e(c)}</button>'
        for c in categories
    )

    cards = []
    for p in PROJECTS:
        if p.get("status") == "Concept":
            tag = '<span class="card__tag">Concept</span>'
        elif p["client"] == "Under NDA" or p["depth"] == "nda":
            tag = '<span class="card__tag">Under NDA</span>'
        else:
            tag = ""
        preview = f' data-preview="assets/video/{p["slug"]}-loop.mp4"' if p.get("preview") else ""
        cards.append(
            f"""    <article class="card" data-category="{e(p['category'])}" data-reveal{preview}>
      <a class="card__link" href="work/{p['slug']}.html">
        <div class="card__media">
          <img src="assets/img/{p['still']}.jpg" alt="{e(p['title'])} — film still" loading="lazy" width="1600" height="1000">
        </div>
      </a>
      <div class="card__row">
        <h2><a href="work/{p['slug']}.html">{e(p['title'])}</a></h2>
        <span class="card__cat">{e(p['no'])} · {e(p['category'])}</span>
      </div>
      <p class="card__sub">{e(p['card'])}</p>
      {tag}
    </article>"""
        )

    doc = (
        head(
            "Work",
            f"Selected films by {SITE['name']} — brand films, product launches and campaigns. {CLIENT_COUNT} client films, {CONCEPT_COUNT} concepts, {ORIGINAL_COUNT} originals.",
            og_image=PROJECTS[1]["still"],
        )
        + header(active="work.html")
        + f"""
<section class="page-head wrap">
  <div class="page-head__kicker">
    <p class="kicker">Index — <span class="kicker--crimson">●</span> {len(PROJECTS):02d} films</p>
    <p class="kicker">{CLIENT_COUNT} client · {CONCEPT_COUNT} concept · {ORIGINAL_COUNT} original</p>
  </div>
  <h1>Selected <em>work.</em></h1>
  <p class="lede">Brand films, product launches and campaigns — plus concepts made on spec and original shorts. Every entry says which it is. The deep studies show the direction and the cut; the lighter entries show the range.</p>
  <div class="page-head__meta">
    <span>Campaign</span><span>·</span><span>Film</span><span>·</span><span>Product</span><span>·</span><span>Fashion</span><span>·</span><span>Beauty</span><span>·</span><span>Food</span>
  </div>
</section>

<section class="act wrap" style="padding-top:0">
  <div class="filters" role="group" aria-label="Filter work by category">
      {filters}
    <span class="filters__count" data-filter-count>{len(PROJECTS):02d} of {len(PROJECTS):02d}</span>
  </div>
  <div class="index-grid">
{chr(10).join(cards)}
  </div>
</section>

<section class="close" aria-label="Start a project">
  <div class="wrap close__inner">
    <h2>Something<br>like <em>this?</em></h2>
    <a class="btn" href="contact.html">Start a project <span aria-hidden="true">→</span></a>
    <span class="close__mail">{e(SITE['email'])}</span>
  </div>
</section>
"""
        + footer()
    )
    return doc


def project_page(p: dict) -> str:
    base = "../"
    idx = PROJECTS.index(p)
    nxt = PROJECTS[(idx + 1) % len(PROJECTS)]
    client = "Under NDA" if p["client"] == "Under NDA" else p["client"]

    films = p.get("films") or ([{"src": p["film"], "format": p.get("format", "16:9"),
                                   "runtime": p["runtime"], "poster": p.get("poster")}]
                                if p.get("film") else [])
    if films:
        blocks = []
        for i, f in enumerate(films):
            fmt = f.get("format", p.get("format", "16:9"))
            vert = " player--vertical" if fmt == "9:16" else ""
            poster = f.get("poster") or p.get("poster") or (p["still"] + ".jpg")
            label = (f'<p class="kicker player__label">{e(f.get("label") or f"Film {i + 1:02d}")}'
                     f' · {e(f.get("runtime", p["runtime"]))}</p>\n') if len(films) > 1 else ""
            blocks.append(f"""{label}<figure class="player{vert}" data-reveal>
  <video controls playsinline preload="metadata" poster="../assets/img/{poster}" data-format="{e(fmt)}">
    <source src="../{e(f['src'])}" type="video/mp4">
    Your browser does not support video. <a href="../{e(f['src'])}">Download the film</a>.
  </video>
  <figcaption><span>{e(p['title'])} — {e(f.get('runtime', p['runtime']))}</span><span>{e(fmt)} · MP4 · sound on</span></figcaption>
</figure>""")
        hero = "\n".join(blocks)
    elif p.get("vimeo"):
        hero = f"""<figure class="player" data-reveal>
  <img src="../assets/img/{p['still']}.jpg" alt="{e(p['title'])} — poster frame" width="1600" height="900">
  <button class="player__btn" type="button" data-vimeo="{e(p['vimeo'])}" data-title="{e(p['title'])}">
    <span class="transport__play" aria-hidden="true"></span> Play film
  </button>
  <figcaption><span>{e(p['title'])} — {e(p['runtime'])}</span><span>Vimeo · click to load</span></figcaption>
</figure>"""
    else:
        hero = f"""<figure class="proj-hero" data-reveal>
  <img src="../assets/img/{p['still']}.jpg" alt="{e(p['title'])} — film still" width="1600" height="900">
  <figcaption><span>{e(p['title'])}</span><span>{e(p['runtime'])} · {e(p['year'])}</span></figcaption>
</figure>"""

    if p["depth"] == "nda":
        body = f"""
<div class="locked">
  <div class="locked__panel">
    <div class="locked__mark" aria-hidden="true">NDA</div>
    <div>
      <p class="kicker">Embargoed study</p>
      <h2>This film is under embargo.</h2>
      <p>{e(p.get('nda_note') or 'The client asked us to hold the film until release.')}</p>
      <p>If you are evaluating the studio for a similar project, the board and two excerpts can be shown on a call.</p>
      <a class="btn" href="../contact.html">Request access <span aria-hidden="true">→</span></a>
    </div>
  </div>
</div>
"""
        stills = ""
    else:
        sections = []
        for i, s in enumerate(p["sections"]):
            paras = "\n      ".join(f"<p>{e(t)}</p>" for t in s["paras"])
            quote = ""
            if i == 1 and p.get("quote"):
                quote = f'\n      <blockquote>{e(p["quote"])}</blockquote>'
            sections.append(
                f"""    <section>
      <p class="kicker">{e(s['label'])}</p>
      <h2>{e(s['head'])}</h2>
      {paras}{quote}
    </section>"""
            )
        body = f"""
<div class="wrap">
<div class="proj-body">
  <div class="proj-body__rail">
    <p class="kicker">At a glance</p>
    <dl class="facts" style="margin-top:1.2rem">
      <div class="fact"><dt>Client</dt><dd>{e(client)}</dd></div>
      <div class="fact"><dt>Status</dt><dd>{e(p.get('status', 'Client'))}</dd></div>
      <div class="fact"><dt>Year</dt><dd>{e(p['year'])}</dd></div>
      <div class="fact"><dt>Runtime</dt><dd>{e(p['runtime'])}</dd></div>
      <div class="fact"><dt>Format</dt><dd>{e(p.get('format', '16:9'))}</dd></div>
      <div class="fact"><dt>Role</dt><dd>{e(p['role'])}</dd></div>
    </dl>
  </div>
  <div class="proj-copy">
{chr(10).join(sections)}
  </div>
</div>
</div>
"""
        stills = ""
        if p.get("stills"):
            figs = "\n".join(
                f"""  <figure>
    <img src="../assets/img/{s['img']}.jpg" alt="{e(s['caption'])}" loading="lazy" width="1600" height="900">
    <figcaption>{e(s['caption'])}</figcaption>
  </figure>"""
                for s in p["stills"]
            )
            stills = f"""
<section class="proj-stills wrap" aria-label="Stills">
{figs}
</section>
"""

    sheet_cols = "\n".join(
        f"""    <div class="sheet__col">
      <dl><dt>{e(c['role'])}</dt><dd>{e(c['value'])}</dd></dl>
    </div>"""
        for c in p["credits"]
    )

    doc = (
        head(
            p["title"],
            p["summary"],
            base=base,
            og_image=p["still"],
        )
        + header(base=base, active="work.html")
        + f"""
<section class="page-head wrap">
  <div class="page-head__kicker">
    <p class="kicker"><a href="../work.html">Work</a> — {e(p['no'])} / {e(p['category'])}</p>
    <p class="kicker">{e(p['year'])} · {e(p['runtime'])}</p>
  </div>
  <h1>{e(p['title'])}</h1>
  <p class="lede">{e(p['summary'])}</p>
  <p class="proj-brief"><span class="kicker">Brief</span> {e(p.get('brief', ''))}</p>
  <div class="page-head__meta">
    <span>{e(client)}</span><span>·</span><span>{e(p['role'])}</span><span>·</span><span>{e(p['category'])}</span>
  </div>
</section>

<div class="wrap">
{hero}
</div>
{body}{stills}
<section class="sheet wrap" aria-label="Credits">
  <p class="kicker">Credits — call sheet</p>
  <div class="sheet__grid">
{sheet_cols}
  </div>
</section>

<section class="next wrap" aria-label="Next project">
  <p class="kicker">Next — {e(nxt['no'])} / {len(PROJECTS):02d}</p>
  <a class="next__link" href="{e(nxt['slug'])}.html">
    <div class="next__media"><img src="../assets/img/{nxt['still']}.jpg" alt="{e(nxt['title'])} — still from the film" loading="lazy" width="1600" height="900"></div>
    <div class="next__body">
      <p class="kicker">{e(nxt['category'])} · {e(nxt['year'])}</p>
      <h2>{e(nxt['title'])}</h2>
      <p class="card__sub" style="margin-top:.8rem">{e(nxt['card'])}</p>
    </div>
  </a>
</section>
"""
        + footer(base=base)
    )
    return doc


def about() -> str:
    doc = (
        head(
            "About",
            f"{SITE['name']} is a one-room AI film studio. Direction, render and finish under one roof — {SITE['hours']}.",
            og_image="portrait",
        )
        + header(active="about.html")
        + f"""
<section class="page-head wrap">
  <div class="page-head__kicker">
    <p class="kicker">The studio — <span class="kicker--crimson">●</span> One room</p>
  </div>
  <h1>A one-room studio,<br><em>on purpose.</em></h1>
  <p class="lede">Maverick Hub makes brand films, product launches and campaigns using AI production — directed, cut and graded by one person who has to sign their name to the frame.</p>
</section>

<section class="act wrap" style="padding-top:0">
  <div class="about-grid">
    <div class="about-grid__img" data-reveal>
      <img src="assets/img/portrait.jpg" alt="{e(SITE['founder'])}, founder and director" loading="lazy" width="1100" height="1375">
    </div>
    <div class="about-grid__body" data-reveal>
      <p class="kicker">The founder</p>
      <h2>I direct the film. The models render it.</h2>
      <p>I spent years cutting other people's footage before I started making frames of my own. The part of the job I care about has not changed: deciding what the shot is, and throwing away the version that almost works.</p>
      <p>AI production changed the economics, not the craft. A brand can now afford six consistent films in the time a traditional shoot would take to book a location — but only if someone is directing, not prompting.</p>
      <p>Maverick Hub stays small on purpose. A handful of films at a time, one director, no account layer between you and the cut.</p>
      <div class="studio__sig" style="margin-top:2rem">
        <b>{e(SITE['founder'])}</b>
        <span class="kicker">Founder, director</span>
        <span class="kicker" style="color:var(--ash-dim)">{('Based ' + e(SITE['city']) + ' · ') if SITE.get('city') else ''}{e(SITE['hours'])}</span>
      </div>
    </div>
  </div>

  <dl class="facts" style="margin-top:clamp(2.4rem,6vh,4rem)">
    <div class="fact"><dt>Studio</dt><dd>{e(SITE['name'])} — an AI film studio for brands</dd></div>
    <div class="fact"><dt>Working with</dt><dd>Founders, DTC brands, agencies and in-house brand teams</dd></div>
    <div class="fact"><dt>Engagements</dt><dd>Single films, launch packages, retained campaign work</dd></div>
    <div class="fact"><dt>Typical project</dt><dd>Fixed fee per film</dd></div>
    <div class="fact"><dt>Territory</dt><dd>US / UK / EU, remote</dd></div>
    <div class="fact"><dt>Availability</dt><dd>{e(SITE['availability'])}</dd></div>
  </dl>
</section>

<section class="act wrap" aria-label="How it is made">
  <div class="act__head">
    <p class="kicker">How it's made</p>
    <p class="count">Three stages, every time</p>
  </div>
{pipeline(show_fig=True)}</section>

<section class="act wrap" aria-label="What this is not">
  <div class="proj-body" style="border-bottom:0">
    <div class="proj-body__rail"><p class="kicker">Position</p></div>
    <div class="proj-copy">
      <h2>Not a prompt shop.</h2>
      <p>There is no menu of styles, no per-second rate card and no template library. Every film starts from a treatment written for the specific product, and every frame is judged the way a frame is judged on a shoot: does it hold, and does it mean anything.</p>
      <p>What that buys you is consistency. Six films that look like one campaign instead of six experiments that each look like the model's default taste.</p>
      <blockquote>If it looks like everyone else's AI film, it is not finished.</blockquote>
    </div>
  </div>
</section>

<section class="close" aria-label="Start a project">
  <div class="wrap close__inner">
    <h2>Tell me what<br>the film has <em>to do.</em></h2>
    <a class="btn" href="contact.html">Start a project <span aria-hidden="true">→</span></a>
    <span class="close__mail">{e(SITE['email'])}</span>
  </div>
</section>
"""
        + footer()
    )
    return doc


def contact() -> str:
    doc = (
        head(
            "Start a project",
            f"Send a project brief to {SITE['name']}. Fixed fee per film. Reply within two working days.",
            og_image="portrait",
        )
        + header(active="contact.html")
        + f"""
<section class="page-head wrap">
  <div class="page-head__kicker">
    <p class="kicker">Project brief — <span class="kicker--crimson">●</span> {e(SITE['availability'])}</p>
    <p class="kicker">Reply in two working days</p>
  </div>
  <h1>Tell me what<br>the film has <em>to do.</em></h1>
  <p class="lede">The useful brief is not a moodboard. It is what the film has to achieve, who has to see it, and when it has to be live. Everything else we can work out together.</p>
</section>

<section class="act wrap" style="padding-top:0">
  <div class="brief">
    <aside class="brief__aside">
      <p class="kicker">Direct</p>
      <p style="margin-top:.9rem"><a href="mailto:{e(SITE['email'])}" style="border-bottom:1px solid var(--hair)">{e(SITE['email'])}</a></p>
      <p>Prefer to talk first? Send the brief anyway and say so — a twenty-minute call is usually faster than three rounds of email.</p>
      <p class="mono" style="margin-top:2rem">Fixed fee per film<br>US / UK / EU</p>
      <span class="mono">{e(SITE['hours'])}</span>
    </aside>

    <form class="brief__form" id="brief-form" method="post" action="{e(SITE['form_endpoint'])}" data-endpoint="{e(SITE['form_endpoint'])}" data-email="{e(SITE['email'])}">
      <div class="form-grid">
        <label class="field">
          <span class="field__label">Name <i>required</i></span>
          <input type="text" name="name" autocomplete="name" required aria-required="true">
        </label>
        <label class="field">
          <span class="field__label">Email <i>required</i></span>
          <input type="email" name="email" autocomplete="email" required aria-required="true">
        </label>
        <label class="field">
          <span class="field__label">Company / brand</span>
          <input type="text" name="company" autocomplete="organization">
        </label>
        <label class="field">
          <span class="field__label">Project type</span>
          <select name="type">
            <option value="">Select one</option>
            <option>Product launch film</option>
            <option>Brand / manifesto film</option>
            <option>Campaign — multiple cuts</option>
            <option>Music / artist film</option>
            <option>Something else</option>
          </select>
        </label>
        <label class="field">
          <span class="field__label">Budget <i>required</i></span>
          <select name="budget" required aria-required="true">
            <option value="">Select a range</option>
            <option>$10k–$25k</option>
            <option>$25k–$50k</option>
            <option>$50k+</option>
            <option>Not sure yet</option>
          </select>
        </label>
        <label class="field">
          <span class="field__label">Live by <i>required</i></span>
          <select name="timeline" required aria-required="true">
            <option value="">Select a timeline</option>
            <option>Within 4 weeks</option>
            <option>1–3 months</option>
            <option>This quarter</option>
            <option>Just exploring</option>
          </select>
        </label>
        <label class="field field--full">
          <span class="field__label">What the film has to do <i>required</i></span>
          <textarea name="brief" required aria-required="true" aria-describedby="brief-hint"></textarea>
          <span class="field__hint" id="brief-hint">The product, the audience, the deadline. Links to references or existing assets are welcome.</span>
        </label>
        <label class="field field--full">
          <span class="field__label">Links <i>optional</i></span>
          <input type="text" name="links" inputmode="url" aria-describedby="links-hint">
          <span class="field__hint" id="links-hint">Deck, product page, references — anything that saves a round of email.</span>
        </label>
      </div>

      <label class="hp" aria-hidden="true">Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label>

      <div class="form-foot">
        <button class="btn" type="submit">Send the brief <span aria-hidden="true">→</span></button>
        <p class="form-note">{e(SITE['form_note'])}</p>
      </div>
      <p class="form-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
"""
        + footer()
    )
    return doc


# ---------------------------------------------------------------- build


def main() -> None:
    (ROOT / "work").mkdir(exist_ok=True)

    written = []

    def write(rel: str, content: str) -> None:
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(rel)

    write("index.html", home())
    write("work.html", work_index())
    write("about.html", about())
    write("contact.html", contact())

    for p in PROJECTS:
        write(f"work/{p['slug']}.html", project_page(p))

    # remove project pages that no longer exist in the content file
    keep = {p["slug"] + ".html" for p in PROJECTS}
    for path in (ROOT / "work").glob("*.html"):
        if path.name not in keep:
            path.unlink()

    print(f"built {len(written)} pages for {len(PROJECTS)} projects")
    for rel in written:
        print("  ", rel)


if __name__ == "__main__":
    main()
