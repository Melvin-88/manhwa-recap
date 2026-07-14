# Memoria — AI Content Pipeline

A registry-driven pipeline for producing narrated series with AI-generated images (an "audiobook with pictures" format).

## Why This Structure

Everything in this repository is plain Markdown/JSON. No formats specific to a single LLM. That means:
- Any LLM (Claude, GPT, Gemini, a local model) can read the whole project context just by opening the files.
- The `skills/<name>/SKILL.md` layout is the same format used by **OpenClaw** (`~/.openclaw` looks for folders containing SKILL.md). Whenever automation via OpenClaw happens, these skills plug in directly, with no rewriting.
- Git-friendly: diffs, change history, rollback.

## Structure

`skills/` and `docs/` are shared across every story (a story-agnostic pipeline). A given adaptation's data (registries, episodes, reference images) lives in its own folder under `stories/<story-slug>/`, so different stories never mix.

```
memoria/
├── README.md                    ← this file
├── docs/
│   ├── architecture.md          ← pipeline description, principles, and the multi-story structure
│   ├── business-analysis.md     ← market, copyright, technology, business model
│   ├── pilot-plan.md            ← step-by-step pilot rollout plan + OpenClaw automation plan
│   └── superpowers/
│       ├── specs/                ← architecture design specs
│       └── plans/                ← implementation plans
├── skills/                      ← every pipeline agent as a SKILL.md (OpenClaw-compatible, shared across stories)
│   ├── source-ingestion/
│   ├── master-narrative/
│   ├── scene-intelligence-engine/
│   ├── storyboard-planner/
│   ├── registry-builder/
│   ├── visual-shot-package/
│   ├── prompt-compiler/
│   ├── image-director/
│   ├── narrator-audio-director/
│   └── produce-episode/         ← orchestrates the whole pipeline as one command (takes story_slug)
└── stories/                     ← one folder per adapted story
    └── <story-slug>/            ← e.g. stories/example-story/
        ├── source-material/
        │   └── master-extract.json   ← accumulated source facts (Source Ingestion)
        ├── registries/                ← Single Source of Truth for THIS story only
        │   ├── character-registry.json
        │   ├── location-registry.json
        │   ├── prop-registry.json
        │   ├── camera-registry.json
        │   ├── palette-registry.json
        │   └── style-registry.json
        ├── characters/                ← actual character reference-sheet files
        │   └── CHAR_001/reference.png
        └── episodes/                  ← working files for each of this story's episodes
            └── ep01/
                ├── script.md              ← editorial brief: source URL + deliberate changes
                ├── 00-source-extract.json
                ├── 01-master-narrative.json
                ├── 02-scene-intelligence.json
                ├── 03-storyboard.json
                ├── 04-visual-shot-package.json
                ├── 05-prompt-package.json
                ├── 06-generation-log.json
                ├── generated/             ← actual generated frame files (not URLs)
                ├── audio/
                └── final/
```

**A new story:** create `stories/<new-slug>/` following this same template — no need to change `skills/` or `docs/`.

## Handing This Off to Another LLM or to OpenClaw

**To another LLM:** have it read `docs/architecture.md` + the relevant `registries/*.json` + the needed `skills/<name>/SKILL.md`. That's enough for full context without any chat history.

**OpenClaw:** point `~/.openclaw/skills` (or the corresponding shared-skills path) at this repo's `skills/` folder — every subfolder containing a SKILL.md becomes available to the agent as a separate tool.

## Project Status

Pilot phase. See `docs/pilot-plan.md` for current steps and the checklist.
