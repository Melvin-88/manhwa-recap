# Step-by-Step Pilot Rollout Plan (Original Content)

Goal: ship 3-5 videos in ~4 weeks, verify whether the Memoria pipeline delivers acceptable quality/speed, and get an initial market signal before scaling.

## Week 1 — Foundation

**1.1. Format and niche (1 day).** Pick something adjacent to what's already working (isekai/regression/"power-leveling systems"), but as a fully original serialized story — not a recap of a specific existing title.

**1.2. Tools and accounts (1–2 days):**

| Tool | Purpose | Cost |
|---|---|---|
| Claude (Pro, already have) | Script/narrative, series structure | already paid for |
| ElevenLabs (Creator plan) | TTS narration | ~$22/mo (~100 min of audio) |
| Nano Banana 2/Pro (API) | Characters/scenes, consistency | ~$0.03–0.05/image |
| Seedream 4.5 (API) | img2img variants, angles | ~$0.03/image |
| CapCut or an ffmpeg script | Assembly: images+audio+subtitles | free |
| YouTube Audio Library | Copyright-free music | free |
| Canva | Cover art, thumbnails | $0–13/mo |

**1.3. Registries for the new story (2–3 days).** Fill in `registries/character-registry.json` for 3–5 characters. A character sheet per character: 4-6 reference images (front, profile, full body, close-up, 2 expressions) via Nano Banana 2, no LoRA training.

Time: 4–6 days. Cost: ~$25–35.

## Week 2 — Pilot Video #1

Run the first episode through the whole pipeline (Master Narrative → Scene Intelligence → Storyboard → Registry → Visual Shot Package → Prompt Compiler → Image Director), generator: Nano Banana 2/Seedream. Voice it via ElevenLabs (lock in the voice_id). Assemble the video: Ken Burns effect on static frames + auto-subtitles (Whisper, run locally). Cover art + title + description tuned for niche SEO.

**Benchmark:** if the full cycle takes more than 2-3 days of manual work, simplify the pipeline before scaling.

Time: 5–7 days. Cost: ~$5–10/video.

## Week 3 — Videos #2–4, Finding a Rhythm

Repeat the cycle 2-3 times, shrinking the manual portion: lock in prompt templates by shot type, lock in the script structure, keep a running "what worked" log against retention.

Time: 7–10 days. Cost: ~$15–30.

## Week 4 — Publishing and Analysis

Publish on a regular cadence. Watch the retention graph, CTR, traffic sources. Launch the Telegram channel immediately, from the first video.

**Checkpoint:** videos retaining above ~40–50% → keep scaling. Low retention across the board → the problem is in the script/pacing, not the images.

## Pilot Budget

| Item | Cost |
|---|---|
| ElevenLabs (1 month) | $22 |
| Image generation (20–30/video × 4) | $15–25 |
| Canva Pro (optional) | $0–13 |
| Buffer for revisions | $15–20 |
| **Total** | **~$55–80** |

---

# Automation via OpenClaw (post-pilot)

OpenClaw is a self-hosted gateway for AI agents: runs on your own hardware/VPS, connects to Telegram/Discord/Slack, supports tool calling, browser automation, multi-agent routing, and **skills** (a folder containing a SKILL.md — the format used in this repo's `skills/`).

## Architecture

```
Telegram: "new episode: [topic]"
   ↓
[Narrator Agent] — skill "master-narrative"
   ↓ structured scenes
[Director Agent] — skills "scene-intelligence-engine" + "storyboard-planner"
   ↓ Visual Shot Package
[Registrar Agent] — updates registries/*.json
   ↓
[Generator Agent] — Nano Banana 2 / Seedream API per shot
   ↓ images
[Voice Agent] — ElevenLabs API, a fixed voice_id
   ↓ audio
[Editor Agent] — ffmpeg script → mp4
   ↓
Telegram: "video ready, preview" → approval
```

**Why this is realistic:** the Claude Pro subscription is reused via OpenClaw (`claude auth login`, reusing the Claude CLI — no separate API bill). Node.js/TS experience makes configuring `openclaw.json` and custom skills straightforward. Memoria's registries already map onto the skills format.

**Automate first:** the mechanical TTS and image-generation calls against an already-built Shot Package.
**Keep manual longest:** the script itself and the final video approval — fully automated templated narration is exactly what YouTube demonetizes.

**Build time:** 1–2 weeks, **after** the pilot, not in parallel with it.

## Next Checkpoint

After the pilot: a solid retention/growth signal → build OpenClaw automation to increase release cadence. A weak signal → one more iteration on script/format before automating.
