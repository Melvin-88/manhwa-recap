# Business Analysis: a YouTube Channel for AI Manga/Manhwa Recaps (Project Memoria)

> Research date: July 2026. The market and tools change fast — verify currency before making decisions based on specific figures.

## TL;DR

- The niche is profitable but crowded and risky. RPM is $2–5 in the manhwa-recap segment, sustained by volume (500K–2M views for a viral video). Primary income isn't AdSense — it's Boosty/Patreon/paid Telegram.
- The plan to "make a unique work" by changing names does **not** provide legal protection. Changing details doesn't remove derivative-work status. The practical risk is Content ID/DMCA strikes and YouTube's "inauthentic content" policy effective 2025-07-15.
- As of 2026, reference-conditioned models (Nano Banana 2, Seedream 4.5) give better character consistency without LoRA training than the classic SDXL+LoRA+IP-Adapter+ControlNet stack (those three signals conflict with each other).

## 1. Market and Competition

The dominant format is a long, "stitched-together" recap (isekai/regression/"power-leveling systems"): titles like Solo Leveling, TBATE, Tower of God, Omniscient Reader. Monetization is multi-channel: AdSense + Boosty + paid Telegram (via Tribute) + brand integrations.

English-language benchmarks: *Manga Explained* — ~1.19M views/month, ~$4.66K/month AdSense (vidIQ). *Manhwa Recap Daily* — 34,200 subscribers, ~$1.21 per 1,000 views (low RPM).

Regional factor: views from Ukraine/CIS carry a lower CPM than US/Europe.

## 2. Copyright and YouTube Policy

- **Derivative work:** changing a few details/names doesn't create a new, independent work under US law (Cornell Wex, Copyright Office Circular 14).
- **Fair use:** protects commentary/critique/review (*Campbell v. Acuff-Rose*, 1994), but *Andy Warhol Foundation v. Goldsmith* (2023) narrowed the bounds of transformativeness via market-effect analysis.
- **Content ID ≠ a strike:** Content ID claims revenue automatically; a DMCA strike removes the video; 3 strikes within 90 days = channel termination.
- **Shueisha, 2021:** a wave of strikes turned out to be fraud by a third party impersonating the publisher — showing the system is vulnerable to abuse and operates on a "take down first, sort it out later" basis.
- **The "inauthentic content" policy (effective 2025-07-15):** YouTube explicitly demonetizes "AI-generated content made with generic templates giving the impression of mass production without adding original, authentic insights." This applies directly to the "template → TTS → AI images, produced serially" format.

## 3. AI Technology (2026)

The classic LoRA + IP-Adapter + ControlNet stack conflicts with itself (a documented issue). Reference-conditioned models have displaced that approach:

- **Nano Banana 2/Pro** (Gemini 3.1 Flash Image, February 2026) — up to 5 characters, 14 objects, stable across 8-10+ edits, 3-6 references with no training.
- **Seedream 4.5** — strong for iterative img2img, cheaper (~$0.03/image).
- **Midjourney Niji 7** (January 2026) — the best artistic aesthetic, weaker consistency.

Recommended cycle: Seedream 4.5 for variants → Nano Banana Pro for final polish.

**Copyright risk of img2img from actual manga pages:** riskier than generating from text descriptions. US Copyright Office (May 2025): if the output is "substantially similar to training data inputs," that's a strong argument for infringement of reproduction and derivative-work rights.

## 4. Business Viability

- Per-video cost is a few dollars (ElevenLabs ~$0.10/1,000 characters, images cost cents per frame).
- Time to reach the YPP threshold (1,000 subscribers + 4,000 watch hours/year) is a few months at a fast production pace, but AdSense monetization isn't guaranteed given section 2.
- Top risks in priority order: (1) demonetization for inauthentic content, (2) DMCA strikes/channel termination, (3) niche saturation, (4) algorithmic dependency + low regional CPM.

## Key Conclusion

The "recap + cosmetic changes" plan pulls in two opposite directions at once: the closer to the original, the higher the copyright risk; the more templated automation, the higher the demonetization risk. The safest configuration is **original stories**: zero copyright risk, owned IP, further licensable.

## Recommendations

1. Drop the "1:1 recap + cosmetic changes" plan.
2. Replace Memoria's generator from SDXL/Flux with Nano Banana 2 + Seedream 4.5.
3. Generate characters only from text descriptions, never via img2img from actual manga pages.
4. Pilot on an original story with authorial commentary/analysis as the "authentic insight" layer.
5. Drive viewers to Telegram/Boosty from the very first video (low CPM on CIS traffic).

## Caveats

- Exact metrics for the benchmark channels weren't obtained (Social Blade/vidIQ render via JS) — for precise figures, use the YouTube Data API v3 with a Channel ID.
- Revenue estimates from AI-service guides skew toward marketing; third-party trackers are more reliable but still estimates.
- Legal conclusions are general in nature, not legal advice. US case law on AI copyright is unsettled; Ukrainian/EU law has its own nuances.
- Models update every few months — verify current benchmarks before finalizing the pipeline.
