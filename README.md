[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/DavidTimoteus/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/DavidTimoteus/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# news-image-20261126 — v1

**Bounty:** make.fun `news-image-20261126` — "Sum up 26 November's
world news in one image"
**File:** `entry.png` — 1024×1024 RGB, 170,807 bytes (≤1 MiB)
**SHA-256:** `77bf9899a63e2175eb1431f70533065377e9d04704e5158f66bdfcfa5da2203d`
**Build:** `python3 render_image.py` (100% code-drawn Pillow, no AI
image generation). Deterministic: rendered 2×, byte-identical.
**Status:** v1 complete and self-verified — **ready to be put forward
for submit**. NOT submitted, NOT pushed, NO GitHub repo created, NO
fee paid (per task instructions; the submit session writes a fresh
`main.py`).

## The day in one line

Missiles over Riyadh, a wider nuclear order from Pyongyang — and
Asia's markets rebound as gold and bitcoin climb back.

## Contents

- `render_image.py` — fresh renderer for this day (broadsheet style)
- `entry.png` — the v1 image
- `RESEARCH.md` — 32 researched stories + builder corrections + 5
  new stories verified in the build session
- `SOURCES.md` — per-story verification (outlet + date/time + link +
  framing) for all 31 stories, plus DATE CHECK items
- `DESIGN_NOTES.md` — design language, tokens, layout, art decisions
- `AUDIT_DESIGN.md` — skill set used + self-audit findings

## Numbers

- **31 stories** (13 featured + 18 also-on), **8 regions**:
  Europe 4 · Middle East 3 · East Asia 4 · South Asia 2 ·
  SE Asia 3 · North America 9 · Oceania 4 · Global 2.
- Target was 34–38; the strict date rule (event date, not
  republication date) removed more than extra research added.
  No unverified filler was used to pad the count.
- **Africa and Latin America: zero verified 26 Nov stories.**
  The two candidates (Zambia protest ban, CGT Argentina march)
  were dropped — their core events were 17/25 Nov or merely
  scheduled. This is stated honestly here, not hidden.

## Heroes

1. **Gulf war** (ONGOING) — schematic Gulf map (Sanaa–Riyadh–
   Hormuz–Ras Tanura) + dashed missile arc + Brent $94.71.
   Ras Tanura claim (25 Nov) and PIF Tower strike (24 Nov) are
   NOT used as 26 Nov news.
2. **Kim Jong Un** (CONFIRMED) — schematic Korea map +
   centrifuge rings + Hwasan-31 callout; worded "KCNA reports
   Thursday" (slug ambiguity noted in SOURCES.md).
3. **Asia markets rebound** (CONFIRMED) — bar chart Nikkei +1.6% /
   KOSPI +1.9% / Taiwan +1.96% / Hang Seng Tech +4.0% + gold
   $3,600+ / BTC $61K.

## Date discipline (the lesson of v3, rank 2009)

- UCL results (Sporting 2–2 Man Utd, PSG 2–2 Roma, Lille 2–1
  Bayern), Deloitte WA suspension, SpaceX FCC approval, German
  GDP, Macy's parade postponement, Ras Tanura claim, Zambia
  treason charges — all 24–25 Nov or earlier, all named in
  DATE CHECK, none shown as 26 Nov news.
- FedEx Miami is shown ONLY with its UTC time (01:40 UTC Thu;
  20:40 Wed ET). Bogor mine is framed as Thursday's resumed
  search (flood was Mon 23 Nov). Gold is shown as "$3,600+"
  (KuCoin) with the Reuters $3,566 discrepancy noted in
  SOURCES.md. The Hormuz mine claim is labelled CLAIM (Iran's
  claim, not a confirmed fact).
