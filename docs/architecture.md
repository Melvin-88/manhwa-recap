# Memoria — Architecture & Agent Specification v1.0

> Migrated from `Memoria_AI_Pipeline_Architecture_Agent_Specification_v1.docx`. This file is the source of truth for this document; the docx is no longer edited.

## Purpose

This document defines the current architecture of the Memoria AI production pipeline: each agent's responsibility, data flow, registries, and design principles. It is the primary onboarding specification for another AI agent working on this codebase.

## Documentation Policy

All content under `skills/`, `docs/`, and any implementation plans/specs is written in **English**, regardless of what language is used to converse with the user. Conversations may happen in any language; the durable artifacts (skill rules, architecture docs, plans) do not.

Memoria is a **story-agnostic pipeline tool**. `skills/`, `scripts/`, and `docs/` are the product; any given story under `stories/<story-slug>/` is disposable working data used to exercise and validate the pipeline. Every rule, example, or lesson written into a skill file must be phrased as a **generic, checkable principle** — never as a reference to a specific story's shot IDs, scene IDs, character names, prop names, or narrative content. If a defect is discovered while testing against one story, generalize it to the class of defect before writing it down (e.g. "a plot-critical object's size must be pinned to an explicit scale reference" rather than naming the object or the shot that revealed the problem).

## Project Vision

Memoria is a registry-driven cinematic image generation pipeline. The narrative is the single source of truth. Every stage transforms structured information without inventing facts that aren't present upstream.

## Core Principles

- **Narrative First** — the story drives everything; visuals serve it, not the other way around
- **Single Source of Truth (Registry)** — characters/locations/style are defined once and referenced, never redefined ad hoc
- **Registry-driven workflow** — every stage reads from registries instead of inventing details on the fly
- **No hallucinations** — no agent adds facts that aren't present in the narrative
- **Visual continuity** — a character/location looks the same across shots
- **Separation of responsibilities** — each agent owns exactly one responsibility

## Pipeline

```
Source Ingestion
   ↓
   ├──→ Registry Builder (on-demand)
   ↓
Master Narrative
   ↓
   ├─── Visual branch ───────────────────────────┐
   │  Scene Intelligence Engine                  │
   │     ↓                                       │
   │  Storyboard Planner ←── Registry Builder     │
   │     ↓                                       │
   │  Visual Shot Package                        │
   │     ↓                                       │
   │  Prompt Compiler                            │
   │     ↓                                       │
   │  Image Director → generate_image (MCP)      │
   │                                              │
   └─── Audio branch ────────────────────────────┐│
      Narrator / Audio Director                  ││
        ↓                                        ││
      create_voice + generate_audio (MCP)        ││
                                                   ↓↓
                                              Assembly
                                        (mechanical ffmpeg script,
                                         not an LLM agent)
```

### Source Ingestion
Transforms a source (web novel/manhwa) into structured facts without ever storing the original text verbatim. Operates at the whole-work level: facts accumulate in batches by volume in `source-material/master-extract.json` (scoped to that story's own folder — see "Structure for Multiple Stories"), rather than being re-derived per episode. Each ingested chapter also produces a detailed `source-material/v<N>/c<M>-detailed.json` (substantially richer than the one-line beat entries — sensory detail, appearance, paraphrased dialogue) for fast reuse later without re-fetching the source. Gaps (e.g. a character's appearance not yet described) are filled automatically and flagged as `auto_generated_fields`, without pausing on every open question — a summary goes to the human for confirmation after each batch completes. The episode-level `00-source-extract.json` is a slice (`beat_range`) of `master-extract.json`, not a separate ingestion run. Never stores the original source text verbatim — only facts and short original phrasing.

**Onboarding a new story** (one-time, before the first ingestion pass): 1) the human provides a link to the source → 2) fix the narration language(s) in `story-config.json` → 3) Source Ingestion collects the entire currently-published work, volume by volume (not an arbitrarily small batch). From there: Produce Episode for a specific episode (per-volume processing: scripts, prompts, generation), and finally a human double-check of the finished video (CHECKPOINT 5). Details: `skills/source-ingestion/SKILL.md`, section "Onboarding a New Story".

### Master Narrative
Turns Source Ingestion's facts into a structured narrative in its own prose. Input: `00-source-extract.json` + `script.md`. Output: narrative scenes. Never defines visuals.

### Scene Intelligence Engine
Extracts: scene intent, emotional arc, chronology, continuity, entities, environment logic.

### Storyboard Planner
Breaks scenes into cinematic shots and visual beats. Determines cameras, composition goals, pacing.

### Registry Builder
Maintains immutable registries: Character, Location, Prop, Camera, Palette, Style. Acts as the Single Source of Truth. Invoked on demand — first right after Source Ingestion, again during Storyboard Planner. A new character gets a reference sheet (generated by Image Director) before it can appear in a story shot, and only then is marked `locked:true`.

### Visual Shot Package
Merges the storyboard with registry data into complete visual specs. Contains: camera, lighting, composition, continuity, render constraints, memory images, emotional arc. **Does not generate prompts.**

### Prompt Compiler
Takes a Visual Shot Package + Registry. Resolves conflicts, expands registry locks, builds prompts for the configured `generation_backend` from the style registry.

### Image Director
Takes compiled prompts. Applies the project's Style Preset, validates consistency, calls the generator (`generate_image`/`upscale_image` for the pilot). **Never redesigns characters or environments.** Shots containing a registered character always pass its `reference_sheet_path` as a reference image to the generator (the `character_reference_model` from `style-registry.json`) for face/design consistency across shots; shots without characters may use a simpler model with no reference input.

### Narrator / Audio Director
Parallel audio branch. Turns Master Narrative scenes into narration/dialogue text, generates voice via `create_voice`/`generate_audio` using each character's locked `voice_id`. Independent of the visual branch.

### Assembly
A mechanical ffmpeg script, not an LLM agent. Assembles images per each shot's `pacing_note` + the audio track + subtitles into the final mp4.

## Registry System

| Registry | Purpose |
|---|---|
| CHAR | Canonical character definitions (appearance, character sheet, voice_id) |
| CRE | Recurring non-human creatures/monsters (no dialogue/voice_id), reference sheet only when `recurring: true` |
| LOC | Locations and their visual characteristics |
| PROP | Recurring objects/items, optional `reference_image_path` for visually distinctive ones |
| CAM | Camera presets (angle, lens, movement) |
| PAL | Color palettes by scene/mood |
| STYLE | Global project style |

### Reference Sheets: a Turnaround, Not a Portrait

A character's (or recurring creature's) reference image is a single "turnaround" sheet with multiple angles (front, 3/4, profile, back if needed) and 2-3 facial expressions within one outfit — not a single front-facing portrait. Rationale: given only a front view, the generator invents arbitrary details for side/back shots (e.g. a ponytail that isn't in the reference) — a turnaround eliminates that mismatch.

### Character Appearance Versions (`appearance_states`)

When the story irreversibly changes a character's appearance (new outfit, new weapon, injury, transformation), Registry Builder adds a new entry to that character's `appearance_states[]` with its own reference sheet and `valid_from_scene`. When generating a shot, Image Director picks the version whose `valid_from_scene` is the latest one that has already occurred for the current shot's scene — never a stale version, never one from the future. The old version stays in the array (still needed for shots from earlier scenes). Full field contract: `skills/registry-builder/SKILL.md`.

## Current JSON Artifacts

`00-source-extract.json` → `01-master-narrative.json` → `02-scene-intelligence.json` (+ in parallel `audio/02b-narration-script.json`) → `03-storyboard.json` → `04-visual-shot-package.json` → `05-prompt-package.json` → `06-generation-log.json` (+ `audio/generation-log.json`) → `final/<episode_id>.mp4`. Full field contract for each file lives in the corresponding `skills/<name>/SKILL.md`, Output section.

## Structure for Multiple Stories

`skills/` and the pipeline itself are story-agnostic (shared across any story). But a given story's data (registries, episodes, character reference images, source facts) is tied to one specific adaptation and must never mix with another story's data. So each story gets its own isolated folder:

```
stories/<story-slug>/           ← e.g. stories/example-story/
├── source-material/
│   └── master-extract.json     ← accumulated source facts (Source Ingestion)
├── registries/                 ← Character/Location/Prop/Camera/Palette/Style — for THIS story only
├── characters/
│   └── CHAR_NNN/
│       └── reference.png        ← the actual reference sheet file (not a URL!)
└── episodes/
    └── epNN/
        ├── script.md
        ├── 00-...06-....json     ← pipeline artifacts
        ├── generated/            ← actual generated episode frame files
        ├── audio/
        └── final/
```

**Why files, not URLs:** images/audio returned by `generate_image`/`generate_audio` (MCP) first arrive as temporary URLs on a third-party CDN. These links can expire or become unavailable. So Image Director (and Narrator/Audio Director) **always download the actual file** into the story's folder (`characters/CHAR_NNN/reference.png`, `episodes/epNN/generated/SHOT_NNN.png`) and record a **local relative path** in registries/logs, never a temporary URL.

**`stories/` is not committed to git.** The repository only versions the story-agnostic pipeline architecture (`skills/`, `scripts/`, `docs/`) — specific stories (registries, episodes, generated frames/audio/video, source material) are working data for one adaptation, not part of the shared process. `stories/` is entirely in `.gitignore`; all the files described above stay on local disk without being versioned.

**Creating a new story:** copy this structure under a new `<story-slug>` and run onboarding (link → language(s) → full volume-by-volume ingestion of the work) — see "Onboarding a New Story" under Source Ingestion above. `skills/` and `docs/` stay shared; nothing in them needs to change.

## Design Decisions

- Each agent owns exactly one responsibility.
- Registries are immutable within a single episode.
- Prompt generation is separated from visual planning.
- Style is applied AFTER prompt compilation, not before.

## Future Expansion

Prompt Optimizer, Continuity Resolver, Animation, Video, 3D support.
