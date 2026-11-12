# StockSage demo video — verification note

**Verified:** 2026-11-12 ~19:00 WAT (after final build)
**Video:** `stocksage-demo.mp4` (companion captions: `stocksage-demo.srt`; script: `script-final.md`)

## File checks (ffprobe)

| Check | Result |
|---|---|
| Duration | **131.00 s** (target ~110–130 s; 1 s over target, under X's 2:20 / 140 s limit) |
| Resolution | **1280×720**, 30 fps |
| Video codec | H.264 (`libx264`, CRF 20) |
| Audio codec | AAC 128 kb/s, mono, 16 kHz |
| File size | 3,299,389 bytes (~3.3 MB) — sane for 131 s at 720p |
| Streams | video + audio present |
| Plays / decodes | Yes — full decode to null succeeded; 9 frames extracted at 5/15/35/50/70/95/108/120/128 s and inspected visually |

## Audio checks

- Voiceover present throughout: `silencedetect` (noise −40 dB, min 1 s) found **0** silent gaps ≥ 1 s.
- `volumedetect`: mean volume **−16.7 dB**, max **−2.3 dB** (no clipping).
- Voice is the free offline `flite` TTS (voice `slt`), sped up 1.18× with `atempo`. It is plainly synthetic/robotic — no human voice was available on this VM and no paid API or key was used.

## On-screen numbers vs live state (`data/state.json`, fresh run as of 2026-11-12T18:18:01Z)

| On screen / spoken | Live state | Match |
|---|---|---|
| Top stock GOOGLc (Alphabet Inc.), score **90.48** / 100 | `scores[0]` GOOGLc 90.48 | ✓ |
| GOOGLc components on-chain 85.09 / momentum 90.35 / market 97.81 (why-panel) | components 85.09 / 90.35 / 97.81 | ✓ |
| #2 AMZNc 87.81, #3 SPCXc 85.40, #4 AMDc 85.39 (research table) | same | ✓ |
| Portfolio total **$100,079.72**, cash $0, **10 positions** | `portfolio.total_value_usd` 100079.72, 10 positions | ✓ |
| Largest holding GOOGLc **13.37%** ($13,380.53) | positions[0] 13.37% | ✓ |
| Latest decision: **hold MSTRc**, 2026-11-12 18:18 UTC | `decisions[-1]` hold MSTRc, ts 2026-11-12T18:18:01Z | ✓ |
| Reason verbatim: "Held MSTRc: target 6.9% is within 5pp of current 7.2%." (spoken + captioned + shown in decisions table) | `decisions[-1].reason` — exact string | ✓ |
| Universe **338** tokenized stocks, **72** minted, **57** scored (dashboard badge + narration) | `universe` {count 338, minted 72}, 57 scores | ✓ |
| CLI shot: `python3 -m stocksage decisions \| tail -6` + its real output | output captured from the real CLI run at build time; last line matches `decisions[-1]` | ✓ |
| Closing card: base.org/stocksmaxxing | Verified hackathon page from README (no repo URL exists for this project — none invented) | ✓ |

## What the visuals are

- Research / why-panel / portfolio / decisions / scoring shots: **real screenshots of the live dashboard** (headless Chromium driving `http://127.0.0.1:8000/`, state as of 18:18:01Z). No mockups, no invented numbers.
- CLI shot: real output of `python3 -m stocksage decisions | tail -6`, rendered as a terminal screen.
- Title/closing cards: plain title screens (no data on them).
- All shots are static full frames. An early Ken Burns pan was dropped: it cropped the dashboard header mid-pan.
- Captions are burnt in (libass, DejaVu Sans 20 pt, bottom-centre) AND shipped as the `stocksage-demo.srt` sidecar (29 entries). Caption text matches the spoken words (punctuation-only differences: em-dashes in captions, pauses in speech; "5pp"/"13.37%" in captions vs "5 percentage points"/"13.37 percent" spoken).

## Known limitations / deviations from the brief

1. **Duration 131.00 s** — 1 s over the 110–130 s target (under X's 2:20 limit). The untrimmed narration read 170 s; trims + 1.18× TTS tempo brought it to 131 s.
2. **Voiceover is synthetic (flite `slt`)** — clearly robotic, sped up 1.18×. Intelligible, but a human re-record would sound better.
3. **No repo URL exists** for StockSage (not a git repo; no GitHub link in the README), so the closing card uses the verified hackathon page `base.org/stocksmaxxing` instead. Nothing was invented.
4. **Narration trims** vs the original script (documented in `script-final.md` production note): same facts, fewer words — Segment 2, 3, 4, 5, 6, 7, 8 trimmed; the verbatim MSTRc reason quote is kept in full.
5. **Not done:** posting on X, submitting any form, launching a token, signing any transaction — none of these were attempted (out of scope for this task).
6. Dashboard server was stopped after capture; the video files are self-contained and do not depend on it.

## Build artefacts (for reproducibility)

- `capture.py` — Playwright + headless Chromium (`chromium-headless-shell`, installed via pip venv `/tmp/pw-venv`) dashboard screenshots.
- `cards.py` — title/closing/CLI HTML renders. Note: the VM's bundled browser (`/opt/meta-chromium/chrome`) refuses headless launch ("Hatch WebGL domain policy is required"); the Playwright headless shell was used instead.
- `build_video.py` — voiceover (flite), SRT, segment render, concat, final encode.
- `shots/` — source screenshots; `work/` — per-segment WAVs/MP4s and timings.
