# MAVERICK HUB — asset manifest

The site now runs on your footage. Everything is local: stills in `assets/img/`,
films and hover loops in `assets/video/`. No Vimeo, no third-party player.

Originals stay untouched in `../ALL ASSETS/`. This folder holds web versions only.

---

## 1. Films (12)

| File | Project | Format | Length |
| --- | --- | --- | --- |
| `assets/video/stake-poker.mp4` | Stake Poker — Film 01, the table | 9:16 | 01:00 |
| `assets/video/stake-poker-b.mp4` | Stake Poker — Film 02, the app | 9:16 | 00:54 |
| `assets/video/watchers.mp4` | Watchers | 2.35:1 (in a 16:9 frame) | 01:04 |
| `assets/video/hermanos-tacos.mp4` | Hermanos Tacos | 9:16 | 00:15 |
| `assets/video/main-ai.mp4` | Main AI | 16:9 | 01:11 |
| `assets/video/midea.mp4` | Midea | 16:9 | 00:30 |
| `assets/video/pandora.mp4` | Pandora | 9:16 | 00:18 |
| `assets/video/rhode.mp4` | Rhode | 9:16 | 00:15 |
| `assets/video/alo.mp4` | Alo | 9:16 | 00:11 |
| `assets/video/kayali.mp4` | Kayali | 9:16 | 00:25 |
| `assets/video/escato.mp4` | ESCATO | 9:16 | 00:15 |
| `assets/video/moni-blat.mp4` | Moni Blat | 16:9 | 00:10 |
| `assets/video/final-2.mp4` | Final 2 | 16:9 | 00:23 |

Every project page plays its own file with native controls — click to play, no autoplay,
no cookies. Vertical films are rendered in a 9:16 player so they are not cropped.

**To replace a film:** keep the filename, export H.264 MP4 at 720p or 1080p with AAC
audio and `+faststart`. Nothing else needs to change.

Encoding used here:

```bash
ffmpeg -i input.mp4 -vf "scale=-2:720" \
  -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart assets/video/<slug>.mp4
```

For a vertical film use `scale=720:-2` instead. `veryfast` at CRF 23 keeps a 720p
minute near 8–17 MB; `-preset slow` looks marginally better and takes a few times
longer — worth it only if you are re-encoding by hand.

## 2. Hover loops

`assets/video/<slug>-loop.mp4` — 5 seconds, silent, 960×540 (720 tall for vertical films),
CRF 28. These play on the Work index when a card is hovered, desktop only, and never
under reduced motion or Save-Data. If a loop is missing the card simply shows its still.

## 3. Stills

All are 2000 × 1125 JPEG except the vertical posters (`v-<slug>.jpg`, 9:16),
already graded. Framed on ink where the source is vertical
or scope — those are deliberately diptychs, not crops.

| File | Project | Source frame |
| --- | --- | --- |
| `p01.jpg` | Stake Poker | diptych: table from above, portrait |
| `p02.jpg` | Watchers | cockpit window, shot 5 |
| `p03.jpg` | Hermanos Tacos | taco dip, two frames |
| `p04.jpg` | Main AI | figure in the dark, 00:44 |
| `p05.jpg` | Midea | coffee machine |
| `p06.jpg` | Pandora | wrist and daylight |
| `p07.jpg` | Rhode | two looks |
| `p08.jpg` | Alo | street, two frames |
| `p09.jpg` | Kayali | red bottle, two frames |
| `p10.jpg` | ESCATO | can, two frames |
| `p11.jpg` | Moni Blat | bag on the back seat |
| `p12.jpg` | Final 2 | dog in the field |

Case-study stills: `s01`–`s03` Stake Poker (table, app, the read), `s04`–`s06` Watchers,
`s07`–`s09` Hermanos Tacos. `process.jpg` (1920 × 1080) is the pipeline band frame —
a figure over a cracked floor. `hero.jpg` (2400 × 1350) is the Watchers station frame.
`portrait.jpg` (1100 × 1375) is cropped from your studio portrait.

Replace any of these in place, same filename and ratio. Keep them under ~300 KB.

## 4. Descriptions and briefs

Each film's copy lives in `content/projects.json`:

- `brief` — the one-line ask, shown under the title on the project page
- `summary` — the index/lede sentence
- `card` — the line under the title on the Work index
- `sections` — the case-study body (label, head, paragraphs)
- `quote` — the pull quote (optional)
- `stills` — captions for the three supporting frames
- `credits` — the call sheet

All copy is written from the footage itself. Nothing claims a metric, an award or a
result. Edit the JSON and run `python3 tools/build.py`.

## 5. Still to fill in

| Field | Where |
| --- | --- |
| `[YOUR NAME]` | `content/site.json` → `founder`, plus every credit row |
| `[CITY]` | `content/site.json` → `city` |
| `maverickplushub@gmail.com` | `content/site.json` → `email` |
| Social URLs (`#`) | `content/site.json` → `social` |
| `url` (for canonical/OG) | `content/site.json` → `url` |
| `form_endpoint` | `content/site.json` → `form_endpoint` |

## 6. The concept label

Seven films are brand studies made on spec (Midea, Pandora, Rhode, Alo, Kayali, ESCATO,
Moni Blat). The site labels them **Concept** and the copy says "not commissioned".
If any of those were paid work, change its `status` to `Client` and its `client` to the
brand name — the labels and the Work index counts update on rebuild.
