# MAVERICK HUB

A static portfolio for an AI film studio: brand films, concepts and original shorts.
Hand-written HTML, CSS and JavaScript. No framework, no runtime dependencies, no tracking,
no third-party player.

---

## What is in it

- **Home** — hero, three flagship rows, scrubbed manifesto, three-stage pipeline,
  flagship study, the range rail, studio block, close.
- **Work** — 12 films with category filters and hover loops.
- **Project pages** — 3 deep case studies (Stake Poker, Watchers, Hermanos Tacos; Stake
  carries its two finished vertical cuts on one page),
  1 original narrative with a note (Main AI), 7 concept films, 1 original short.
- **About** and a **project-brief form**.
- All films play locally from `assets/video/` with native controls. Vertical work gets
  a 9:16 player so nothing is cropped.

## Run it locally

```bash
cd maverickhub
python3 -m http.server 8000
# http://localhost:8000
```

Any static server works; the paths are relative.

## Rebuild the pages

```bash
python3 tools/build.py
```

Output (committed, ready to deploy):

```
index.html · work.html · about.html · contact.html
work/stake-poker.html · work/watchers.html · work/hermanos-tacos.html · … (12)
```

Content:

- `content/site.json` — name, email, city, founder, availability, social, form endpoint.
- `content/projects.json` — the 12 films: copy, brief, format, status, film path (`films`
  for projects with more than one film),
  sections, stills, credits.
- `tools/build.py` — templates plus the copy that appears once (home, About, Contact).

## Structure

```
maverickhub/
├── index.html · work.html · about.html · contact.html
├── work/                     12 project pages
├── content/
│   ├── site.json
│   └── projects.json
├── tools/build.py             static generator (no dependencies)
├── assets/
│   ├── css/main.css           design system + components
│   ├── js/site.js             header, reveals, manifesto, rail, filters, loops, form
│   ├── fonts/                 Instrument Serif, Geist, Geist Mono (self-hosted woff2)
│   ├── img/                   hero, portrait, p01–p12, s01–s09, v-* posters, grain, favicon
│   └── video/                 12 films + 12 hover loops
├── ASSETS.md                  every slot, every spec, how to replace
└── README.md
```

## Design system

- **Colour** `#0B0B0C` ink · `#E9E6DE` bone · `#8A857C` ash · `#96131F` darkroom crimson.
- **Type** Instrument Serif for display, Geist for text, Geist Mono for every number,
  label and credit. Self-hosted, `font-display: swap`.
- **Motion** CSS transitions plus one scroll-linked effect (the manifesto). No GSAP,
  no Lenis, no scroll hijacking. Everything stops under `prefers-reduced-motion`.
- **Texture** 3.5% grain and a vignette, both decorative and `aria-hidden`.

## Behaviour, accessibility, performance

- Skip link, landmark structure, one `h1` per page, labelled fields, visible focus.
- Mobile nav locks scroll, closes on Escape or link click, reports `aria-expanded`.
- Content and links work without JavaScript; reveals are gated behind a `.js` class.
- Stills are sized and lazy-loaded; the hero is `fetchpriority="high"`.
- Films are `preload="metadata"` — the browser fetches enough to show a frame, not the file.
- Hover loops are desktop/fine-pointer only, skipped for reduced motion and Save-Data.
- No analytics, no cookies, no third-party requests.

## The project brief form

1. Create a form at a provider (Formspree, Basin, Netlify Forms, …).
2. Put its POST URL in `content/site.json` → `"form_endpoint"`.
3. Rebuild. The form posts `FormData` with `Accept: application/json`.

With no endpoint it validates, then opens a pre-filled `mailto:` to the address in
`site.json` and says so. Honeypot field (`website`) and an `aria-live` status line in
both paths. No key is stored in the page.

## Deploy

Upload the folder to any static host (Netlify, Cloudflare Pages, GitHub Pages, S3).
No build step on the host.

**Bandwidth note:** the films total about 57 MB and only load when someone presses
play, but static hosts usually measure video bytes. If you expect traffic, put
`assets/video/` behind a CDN or move the films to Vimeo and set `vimeo` instead of
`film` per project — the template still supports that path.

Optional caching (Netlify `_headers`): `assets/*` immutable for a year, HTML `no-cache`.
Filenames are not hashed, so purge the CDN when you replace media in place.

## Before it goes live

- Replace `maverickplushub@gmail.com` and set `city` in `content/site.json`.
  Credits inherit `[YOUR NAME]` from the content file — edit them there, not in the HTML.
- Point the social links somewhere, or remove them.
- Confirm the **Concept** labels: seven brand films are marked as spec work. If any were
  commissioned, change `status`/`client` in `content/projects.json`.
- Set the form endpoint and send yourself a test brief.
- Add `"url"` to `site.json` so canonical and share tags are absolute.
