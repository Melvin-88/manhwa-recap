# Memoria — Execution Pipeline Design (v2)

> Status: approved for implementation. Next step: an implementation plan (superpowers:writing-plans).

## Context and Decisions This Design Builds On

At the time of writing, none of the 7 stages in `architecture.md` had ever been executed — there were only prose agent specs (`skills/*/SKILL.md`), empty registry scaffolding, and an empty `episodes/ep01/` template. This is a design for exactly how the pipeline will execute — manually for now, with room for automation (OpenClaw) later without rewriting the data contract.

Key decisions made during brainstorming:

1. **The story source is a recap/adaptation of existing published works** from external sources (web-novel/manhwa aggregators by URL, e.g. ranobelib.me), NOT fully original stories. This is a deliberate choice with an accepted risk (derivative-work status under copyright law, possible DMCA action, YouTube's "inauthentic content" policy effective 2025-07-15 — documented in `docs/business-analysis.md`). Risk mitigation is built into the architecture via the new Source Ingestion stage (section 2).
2. **The image/audio generator for the pilot is Claude's built-in MCP tools** (`generate_image`, `generate_video`, `generate_audio`, `create_voice`, `upscale_image`, etc.), rather than separate Nano Banana 2/Seedream 4.5/ElevenLabs APIs. `generator_config` in the style registry stores this as a swappable setting, so switching to direct APIs later requires no rewrite of Prompt Compiler/Image Director.
3. Splitting the narrative into scenes and scenes into shots **is retained** — each `generate_image` call corresponds to exactly one shot with its own composition/camera/continuity; without that split there'd be nothing to map individual generator calls onto.

## 1. Full Pipeline

```
Source Ingestion (NEW)
   ↓ 00-source-extract.json (facts, not the original text)
   ├──→ Registry Builder (on-demand: new characters/locations with adapted names)
   ↓
Master Narrative
   ↓ 01-master-narrative.json (scenes written in original prose based on facts)
   │
   ├─── VISUAL BRANCH ─────────────────────────────────────────┐
   │  Scene Intelligence Engine → 02-scene-intelligence.json   │
   │     ↓                                                     │
   │  Storyboard Planner → 03-storyboard.json  ←── Registry Builder (on-demand)
   │     ↓                                                     │
   │  Visual Shot Package → 04-visual-shot-package.json        │
   │     ↓                                                     │
   │  Prompt Compiler → 05-prompt-package.json                 │
   │     ↓                                                     │
   │  Image Director → generate_image / upscale_image (MCP)    │
   │     ↓ 06-generation-log.json                               │
   │                                                            │
   └─── AUDIO BRANCH (NEW) ─────────────────────────────────────┐│
      Narrator / Audio Director                                 ││
        ↓ audio/02b-narration-script.json                       ││
      create_voice + generate_audio (MCP)                       ││
        ↓ audio/generation-log.json                             ││
                                                                   ↓↓
                                                              Assembly
                                                       (mechanical ffmpeg script,
                                                        NOT an LLM agent)
                                                              ↓
                                                          final/epNN.mp4
```

### New/Changed Agent Responsibilities

**Source Ingestion (new skill, `skills/source-ingestion/SKILL.md`)**
- Input: one or more source-chapter URLs (one iteration = one range of chapters covering one episode; no bulk-scraping an entire novel at once).
- Processing: read the chapter (`WebFetch`), extract structured facts — characters (original name → adapted name, role, traits), world/setting, key plot events in short original phrasing.
- **Hard rule:** the original source text is never stored verbatim in any repository file. The output must be substantially shorter and retold in original words — a sequence of facts, not a sequence of paraphrased sentences tracking the original.
- Output: `00-source-extract.json` (see section 2) + `adaptation_notes` (exactly what was changed/compressed/renamed relative to the source — needed for checkpoint 0).

**Master Narrative (updated responsibility)**
- Input is now `00-source-extract.json` (facts), not a ready-made human script. Writes scene prose in its own words based on the facts. This is where the transformation/compression actually happens, not Source Ingestion.
- The role of `script.md`/the human brief changes: it's no longer the plot itself, but an **editorial brief** — which source chapters the episode covers, which deliberate changes to make (e.g. "compress this arc into one scene," "change character X's motivation"). The file keeps the name `script.md` to minimize disruption to the existing structure.

**Narrator / Audio Director (new skill, `skills/narrator-audio-director/SKILL.md`)**
- Previously, narration wasn't part of the agent pipeline at all (in `pilot-plan.md` it was a manual "record via ElevenLabs" step outside the flow). Now it's a separate branch, parallel to the visual one, starting right after Master Narrative (independent of Storyboard/Shot Package).
- Input: scenes from `01-master-narrative.json` (summary, emotional_beat) + `voice_id` from `character-registry.json`.
- Output: `audio/02b-narration-script.json` (lines/narration per scene) → calls to `create_voice` (once per character, cached) + `generate_audio`.
- Rule (by analogy with Image Director): if a scene's emotional tone diverges significantly from that character's previous voice usage, flags it for manual review rather than generating silently.

**Registry Builder** — not a sequential stage but an on-demand service. Now called for the first time right after Source Ingestion (creates unlocked character entries with adapted names), and again during Storyboard Planner whenever new locations/props appear. Its position in the diagram marks the checkpoint "every entity the storyboard references has `locked:true`."

**Assembly (new, mechanical, NOT an LLM agent)** — a plain ffmpeg script: images per each shot's `pacing_note` + the audio track + subtitles → mp4. Requires no LLM judgment, so it isn't written up as a SKILL.md.

## 2. Data Contracts and Episode File Structure

```
episodes/epNN/
├── script.md                     ← the human's editorial brief: source URL(s) covering the episode, deliberate changes
├── 00-source-extract.json        ← facts from Source Ingestion (characters/world/events, adaptation_notes)
├── 01-master-narrative.json      ← scenes written in original prose
├── 02-scene-intelligence.json    ← enriched scenes
├── 03-storyboard.json            ← shots per scene
├── 04-visual-shot-package.json   ← complete visual specs
├── 05-prompt-package.json        ← compiled prompts (generator-agnostic, MCP-ready)
├── 06-generation-log.json        ← generate_image/upscale_image log: asset paths, retries, timestamps
├── audio/
│   ├── 02b-narration-script.json ← lines/narration per scene + voice_id
│   └── generation-log.json       ← create_voice/generate_audio log
└── final/
    └── epNN.mp4                  ← Assembly's output
```

File numbering reflects execution order and allows stopping/resuming at any step — a human can open and manually edit an intermediate JSON between stages.

**Schema format:** no separate `.schema.json` validator files (the contract is consumed by an LLM, not by code that validates it). Instead, every `SKILL.md` gets an expanded **Output** section with a concrete example JSON showing field types, rather than today's plain list of field names. This keeps a single source of truth for an agent's contract in the same file as its behavior description.

## 3. Registry Changes

- `character-registry.json`: field `voice_id_elevenlabs` → `voice_id` (the provider is now MCP, no longer tied directly to ElevenLabs). Add a `source_name` field (the original name from the source, for internal adaptation traceability, never surfaced in public-facing content).
- `style-registry.json` → `generator_config`: `primary_model: "nano-banana-2"` → `generation_backend: "claude-mcp-media"`; `fallback_model` stays as a documented but inactive entry for a future switch to direct APIs without rewriting Prompt Compiler/Image Director.
- Location/Prop/Camera/Palette registries: the structure is already sufficient — populating them with data is content work for a specific story, not part of this architectural design.

## 4. Orchestration Model

One new skill/slash-command, `produce-episode`, that runs the full sequence (Source Ingestion → ... → Assembly) within a single Claude session per episode, reading/writing the numbered JSON files from section 2, pausing at checkpoints (section 5).

The file-based nature of the contract means: a human can edit an intermediate JSON by hand at any time, or ask Claude to rerun just one stage (e.g. "regenerate just the storyboard") — with no need for separate slash-commands per agent.

This buys automation-readiness for free: once OpenClaw enters the picture, it calls the same `SKILL.md` files and reads/writes the same files non-interactively — the data model needs no rework.

## 5. Human Confirmation Checkpoints

0. **After Source Ingestion** (new, the most important one given the accepted copyright risk) — the human confirms that `adaptation_notes` shows sufficient transformation (renaming, compression, changes) before the facts flow into Master Narrative.
1. After Master Narrative — confirm the scene breakdown (cheap to redo now, expensive after the later stages).
2. After Registry Builder — confirm new character/location entries before `locked:true` (this rule is already documented in `skills/registry-builder/SKILL.md`).
3. After Prompt Compiler, before Image Director — confirm the shot list before spending generation calls.
4. Image Director / Narrator-Audio Director — automatically flag mismatched frames/voice tone for manual review (the rule already exists for Image Director, extended to the audio branch).
5. After Assembly — a final video review before publishing.

## 6. Success Criterion

Tied to the existing benchmark from `pilot-plan.md`: a full episode cycle in ≤ 2-3 days of manual work. If the checkpoint-driven architecture turns out slower, the first candidate for simplification is merging Scene Intelligence Engine + Storyboard Planner into one call (SIE's output feeds nothing except Storyboard).

## Explicitly Out of Scope for This Design

- Populating the registries with a specific story's real data — that's content work for the next phase, not architecture.
- Legal advice about a specific source/title — the decision to accept the risk has already been made by the user; this isn't legal advice.
- The technical implementation of the Assembly script (ffmpeg commands) — a detail for the next implementation plan.
