# Memoria Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the pipeline architecture from `docs/superpowers/specs/2026-07-11-pipeline-architecture-design.md`: add new skill agents (Source Ingestion, Narrator/Audio Director, Produce Episode), update existing `SKILL.md` files with concrete output schemas, update the registries, restructure the `episodes/ep01/` template under the new file-numbering scheme, and sync `docs/architecture.md` and `README.md`.

**Architecture:** This is a specification repository (Markdown/JSON), not executable code — there are no unit tests in the traditional sense here. Each step's "test" is (a) JSON validity via `python3 -m json.tool`, (b) the presence of required sections/fields via `grep`. Every file is edited in full (files are short, 15-40 lines), so steps provide the complete new file content rather than diff patches.

**Tech Stack:** Markdown, JSON, `python3` (only for JSON validation, already available on the system), `grep`.

## Global Constraints

- The original source text (web novel/manhwa) is never stored verbatim in any repository file — only facts in original wording (from the design spec, section "Source Ingestion").
- Every registry (`registries/*.json`) is its own file; entity types are never mixed.
- `locked:true` registry entries are never changed without explicit human confirmation — this rule already exists in `skills/registry-builder/SKILL.md` and must be preserved across all edits.
- Episode file numbering is fixed: `00-source-extract.json` → `01-master-narrative.json` → `02-scene-intelligence.json` / `02b-narration-script.json` → `03-storyboard.json` → `04-visual-shot-package.json` → `05-prompt-package.json` → `06-generation-log.json` → `final/<episode_id>.mp4`.
- The generator for the pilot is `generation_backend: "claude-mcp-media"` (built-in MCP tools); `fallback_model` stays a documented, inactive alternative.

---

## Task 1: Update Registries (character-registry, style-registry)

**Files:**
- Modify: `registries/character-registry.json` (whole file)
- Modify: `registries/style-registry.json` (whole file)

**Interfaces:**
- Produces: the `voice_id` field (replacing `voice_id_elevenlabs`) and `source_name` in `character-registry.json`; the `generation_backend` field (replacing `generator_config.primary_model`) in `style-registry.json`. Every later task that mentions these fields refers to exactly these names.

- [ ] **Step 1: Rewrite `registries/character-registry.json`**

```json
{
  "_schema_note": "Single Source of Truth for characters. Registry Builder reads/writes here. Prompt Compiler resolves character_id into a description when building a prompt. source_name traces the adaptation from the source (Source Ingestion) and is never surfaced in public-facing content.",
  "characters": [
    {
      "character_id": "CHAR_001",
      "name": "",
      "source_name": "",
      "role": "protagonist | antagonist | supporting",
      "appearance": {
        "age_range": "",
        "build": "",
        "hair": "",
        "eyes": "",
        "distinguishing_features": "",
        "default_outfit": ""
      },
      "personality_visual_cues": "",
      "voice_id": "",
      "reference_sheet_path": "characters/CHAR_001/",
      "generator_notes": {
        "preferred_model": "claude-mcp-media",
        "reference_image_count": 5,
        "consistency_notes": ""
      },
      "locked": false
    }
  ]
}
```

- [ ] **Step 2: Rewrite `registries/style-registry.json`**

```json
{
  "_schema_note": "The project's global Style Preset. One set per series for visual consistency across episodes.",
  "project_style": {
    "art_style": "",
    "line_weight": "",
    "shading_approach": "",
    "reference_images": [],
    "generator_config": {
      "generation_backend": "claude-mcp-media",
      "fallback_model": "nano-banana-2",
      "fallback_notes": "Documented but inactive. Switching to a direct API requires no changes to Prompt Compiler/Image Director, only flipping generation_backend."
    }
  }
}
```

- [ ] **Step 3: Validate JSON**

Run: `python3 -m json.tool registries/character-registry.json > /dev/null && python3 -m json.tool registries/style-registry.json > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 4: Verify the old field names are gone**

Run: `grep -r "voice_id_elevenlabs\|primary_model.*nano-banana" registries/ || echo CLEAN`
Expected: `CLEAN`

- [ ] **Step 5: Commit**

```bash
git add registries/character-registry.json registries/style-registry.json
git commit -m "feat: update registry schemas for MCP generator and source adaptation tracking"
```

---

## Task 2: New Skill — Source Ingestion

**Files:**
- Create: `skills/source-ingestion/SKILL.md`

**Interfaces:**
- Consumes: source URL(s) + the episode's `script.md` (editorial brief)
- Produces: `00-source-extract.json` with the shape `{episode_id, source_refs[], characters_extracted[], world_facts[], plot_beats[], adaptation_notes{renamed[], compressed[], changed[]}}` — Tasks 3/4/5a read exactly these field names.

- [ ] **Step 1: Create `skills/source-ingestion/SKILL.md`**

```markdown
# Skill: Source Ingestion

## Purpose
The pipeline's first stage. Transforms one or more finished source chapters (a web novel/manhwa by URL) into structured facts — characters, world, plot events — without ever storing the original text verbatim. This is where the story's transformation/compression begins.

## Input
- One or more source-chapter URLs covering one episode (one range of chapters at a time, never the whole novel in bulk)
- The episode's `script.md` with an editorial brief (which deliberate changes to make)

## Output
`00-source-extract.json`:
```json
{
  "episode_id": "ep01",
  "source_refs": [
    {"url": "https://example.com/chapter-1", "chapters_covered": "1"}
  ],
  "characters_extracted": [
    {
      "source_name": "",
      "adapted_name": "",
      "role": "protagonist | antagonist | supporting",
      "key_traits": []
    }
  ],
  "world_facts": [],
  "plot_beats": [
    {"beat_id": "BEAT_001", "summary": "", "characters_involved": []}
  ],
  "adaptation_notes": {
    "renamed": [],
    "compressed": [],
    "changed": []
  }
}
```

## Rules
- **The original source text is never stored verbatim in any repository file.** The output is facts and short original phrasing, not paraphrased sentences that track the original.
- The output must be substantially shorter than the source.
- Process one chapter range at a time — never bulk-scrape an entire novel in one call.
- Requires the ability to read a web page (web fetch / browser tool, depending on which agent runs this skill).
- `adaptation_notes` are mandatory and specific — this is the basis for checkpoint 0 (the human confirms the transformation is sufficient before the facts flow into Master Narrative).
- Characters/locations from `characters_extracted` are handed to Registry Builder to create unlocked entries with `source_name` and `adapted_name`.
```

- [ ] **Step 2: Verify the required sections are present**

Run: `grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" skills/source-ingestion/SKILL.md`
Expected: `4`

- [ ] **Step 3: Extract and validate the JSON schema example**

Run: `sed -n '/```json/,/```/p' skills/source-ingestion/SKILL.md | sed '1d;$d' | python3 -m json.tool > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 4: Commit**

```bash
git add skills/source-ingestion/SKILL.md
git commit -m "feat: add Source Ingestion skill"
```

---

## Task 3: New Skill — Narrator / Audio Director

**Files:**
- Create: `skills/narrator-audio-director/SKILL.md`

**Interfaces:**
- Consumes: scenes from `01-master-narrative.json` (fields `scene_id`, `summary`, `emotional_beat`) + `voice_id` from `registries/character-registry.json` (from Task 1)
- Produces: `audio/02b-narration-script.json` and `audio/generation-log.json`

- [ ] **Step 1: Create `skills/narrator-audio-director/SKILL.md`**

```markdown
# Skill: Narrator / Audio Director

## Purpose
The pipeline's parallel audio branch. Turns Master Narrative scenes into narration/dialogue text and generates voice, using each character's locked voice_id. Independent of Storyboard/Visual Shot Package — starts right after Master Narrative.

## Input
- Scenes from `01-master-narrative.json` (`scene_id`, `summary`, `emotional_beat`)
- Each present character's `voice_id` from `registries/character-registry.json`

## Output
`audio/02b-narration-script.json`:
```json
{
  "episode_id": "ep01",
  "narration_lines": [
    {
      "scene_id": "",
      "character_id": "",
      "voice_id": "",
      "text": "",
      "emotional_tone": ""
    }
  ]
}
```

`audio/generation-log.json`:
```json
{
  "episode_id": "ep01",
  "generated_assets": [
    {"scene_id": "", "character_id": "", "audio_path": "", "generated_at": "", "flagged_for_review": false}
  ]
}
```

## Rules
- `voice_id` is created once per character (cached in `character-registry.json`), never regenerated on every call.
- If a scene's emotional tone diverges significantly from that character's previous voice usage, flags `flagged_for_review: true` rather than generating silently (by analogy with the Image Director rule).
- Doesn't define visuals and doesn't depend on shots — it's a parallel branch, not a sequential step after Storyboard Planner.
```

- [ ] **Step 2: Verify the required sections are present**

Run: `grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" skills/narrator-audio-director/SKILL.md`
Expected: `4`

- [ ] **Step 3: Validate both JSON examples**

Run:
```bash
python3 -c "
import re, json
content = open('skills/narrator-audio-director/SKILL.md').read()
blocks = re.findall(r'\`\`\`json\n(.*?)\`\`\`', content, re.DOTALL)
assert len(blocks) == 2, f'expected 2 json blocks, found {len(blocks)}'
for b in blocks:
    json.loads(b)
print('VALID')
"
```
Expected: `VALID`

- [ ] **Step 4: Commit**

```bash
git add skills/narrator-audio-director/SKILL.md
git commit -m "feat: add Narrator/Audio Director skill"
```

---

## Task 4: Update Registry Builder

**Files:**
- Modify: `skills/registry-builder/SKILL.md` (whole file)

**Interfaces:**
- Consumes: `source_name`/`adapted_name` from Source Ingestion (Task 2), fields from `character-registry.json` (Task 1)
- Produces: no change to the external contract — clarifies the invocation trigger (on-demand, first right after Source Ingestion)

- [ ] **Step 1: Rewrite `skills/registry-builder/SKILL.md`**

```markdown
# Skill: Registry Builder

## Purpose
Creates and updates the registries that stay immutable within an episode: Character, Location, Prop, Camera, Palette, Style. The single source of truth for every visual entity in the project.

## Input
A request to create/update an entry in one of the `registries/*.json` files. Called on demand (not a sequential stage): first right after Source Ingestion (new characters with `source_name`/`adapted_name`), again during Storyboard Planner whenever new locations/props appear.

## Output
The relevant registry JSON file, updated. Example for a new character coming from Source Ingestion:
```json
{
  "character_id": "CHAR_002",
  "name": "",
  "source_name": "",
  "role": "protagonist | antagonist | supporting",
  "appearance": { "age_range": "", "build": "", "hair": "", "eyes": "", "distinguishing_features": "", "default_outfit": "" },
  "personality_visual_cues": "",
  "voice_id": "",
  "reference_sheet_path": "characters/CHAR_002/",
  "generator_notes": { "preferred_model": "claude-mcp-media", "reference_image_count": 5, "consistency_notes": "" },
  "locked": false
}
```

## Rules
- Never modifies an existing `locked:true` entry without explicit human confirmation.
- New characters/locations get a character sheet / reference image before being set `locked:true`.
- Each registry is its own file — never mix entity types in one file.
- Character entries created from Source Ingestion must populate `source_name` for adaptation traceability (never surfaced in public-facing content).
```

- [ ] **Step 2: Verify the `locked:true` rule survived**

Run: `grep -q "locked:true" skills/registry-builder/SKILL.md && echo OK`
Expected: `OK`

- [ ] **Step 3: Validate the JSON example**

Run: `sed -n '/```json/,/```/p' skills/registry-builder/SKILL.md | sed '1d;$d' | python3 -m json.tool > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 4: Commit**

```bash
git add skills/registry-builder/SKILL.md
git commit -m "docs: clarify Registry Builder on-demand trigger from Source Ingestion"
```

---

## Task 5a: Update Master Narrative, Scene Intelligence Engine, Storyboard Planner

**Files:**
- Modify: `skills/master-narrative/SKILL.md` (whole file)
- Modify: `skills/scene-intelligence-engine/SKILL.md` (whole file)
- Modify: `skills/storyboard-planner/SKILL.md` (whole file)

**Interfaces:**
- Consumes: `00-source-extract.json` (Task 2)
- Produces: `01-master-narrative.json`, `02-scene-intelligence.json`, `03-storyboard.json` — Tasks 5b and 6 reference these file names and the fields `scene_id`, `shot_id`, `camera_id`.

- [ ] **Step 1: Rewrite `skills/master-narrative/SKILL.md`**

```markdown
# Skill: Master Narrative

## Purpose
Turns Source Ingestion's structured facts into a structured narrative in its own prose. The source of truth for every later pipeline stage. This is where the story's transformation/compression happens — not Source Ingestion.

## Input
`00-source-extract.json` from Source Ingestion (facts: characters, world_facts, plot_beats, adaptation_notes) + `script.md` (the human's editorial brief: episode scope, deliberate changes)

## Output
`01-master-narrative.json`:
```json
{
  "episode_id": "ep01",
  "scenes": [
    {
      "scene_id": "SCENE_001",
      "summary": "",
      "characters_present": [],
      "location": "",
      "emotional_beat": ""
    }
  ]
}
```

## Rules
- Never defines visuals (that's Storyboard Planner's/Visual Shot Package's responsibility).
- Writes its own prose based on the facts in `00-source-extract.json` — doesn't paraphrase the original source text, because that text isn't in the file at all (only facts are).
- Each scene is a standalone unit, ready for further processing by Scene Intelligence Engine.

## Example Invocation (conceptual)
"Here are the facts from 00-source-extract.json for episode 1: [JSON]. Build a Master Narrative in the 01-master-narrative.json format with scenes."
```

- [ ] **Step 2: Rewrite `skills/scene-intelligence-engine/SKILL.md`**

```markdown
# Skill: Scene Intelligence Engine

## Purpose
Analyzes each scene from Master Narrative and extracts the deeper structural data the storyboard needs.

## Input
One scene from `01-master-narrative.json`

## Output
`02-scene-intelligence.json`:
```json
{
  "episode_id": "ep01",
  "scenes": [
    {
      "scene_id": "SCENE_001",
      "scene_intent": "",
      "emotional_arc": "",
      "chronology_position": "",
      "continuity_requirements": [],
      "entities": [],
      "environment_logic": ""
    }
  ]
}
```

## Rules
- Relies only on data from Master Narrative and the registries — invents nothing.
- Doesn't define shot composition (that's Storyboard Planner's job).
```

- [ ] **Step 3: Rewrite `skills/storyboard-planner/SKILL.md`**

```markdown
# Skill: Storyboard Planner

## Purpose
Breaks a scene (already enriched by Scene Intelligence Engine) into concrete cinematic shots.

## Input
An enriched scene from `02-scene-intelligence.json`

## Output
`03-storyboard.json`:
```json
{
  "episode_id": "ep01",
  "shots": [
    {
      "shot_id": "SHOT_001",
      "scene_id": "SCENE_001",
      "camera_id": "",
      "composition_goal": "",
      "pacing_note": "",
      "characters_in_frame": []
    }
  ]
}
```

## Rules
- Every shot has a clear composition goal, not just "show the scene."
- Uses only `camera_id` values from `registries/camera-registry.json` — never invents new presets on the fly (calls Registry Builder if a new one is needed).
```

- [ ] **Step 4: Verify the required sections are present in all three files**

Run: `for f in skills/master-narrative/SKILL.md skills/scene-intelligence-engine/SKILL.md skills/storyboard-planner/SKILL.md; do c=$(grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" "$f"); echo "$f: $c"; done`
Expected: all three lines show `4` (master-narrative also has an `## Example invocation` section, but we're only counting the 4 required ones, so it's still `4`)

- [ ] **Step 5: Validate all three JSON examples**

Run: `for f in skills/master-narrative/SKILL.md skills/scene-intelligence-engine/SKILL.md skills/storyboard-planner/SKILL.md; do sed -n '/```json/,/```/p' "$f" | sed '1d;$d' | python3 -m json.tool > /dev/null && echo "$f VALID"; done`
Expected:
```
skills/master-narrative/SKILL.md VALID
skills/scene-intelligence-engine/SKILL.md VALID
skills/storyboard-planner/SKILL.md VALID
```

- [ ] **Step 6: Commit**

```bash
git add skills/master-narrative/SKILL.md skills/scene-intelligence-engine/SKILL.md skills/storyboard-planner/SKILL.md
git commit -m "docs: add concrete output schemas to narrative/scene/storyboard skills"
```

---

## Task 5b: Update Visual Shot Package, Prompt Compiler, Image Director

**Files:**
- Modify: `skills/visual-shot-package/SKILL.md` (whole file)
- Modify: `skills/prompt-compiler/SKILL.md` (whole file)
- Modify: `skills/image-director/SKILL.md` (whole file)

**Interfaces:**
- Consumes: `03-storyboard.json` (Task 5a), `generation_backend` from `style-registry.json` (Task 1)
- Produces: `04-visual-shot-package.json`, `05-prompt-package.json`, `06-generation-log.json` — Tasks 6 and 7 reference these names.

- [ ] **Step 1: Rewrite `skills/visual-shot-package/SKILL.md`**

```markdown
# Skill: Visual Shot Package

## Purpose
Merges a storyboard shot with registry data into a complete visual spec, ready for prompt compilation.

## Input
- A shot from `03-storyboard.json`
- The matching entries from `registries/character-registry.json`, `location-registry.json`, `prop-registry.json`, `camera-registry.json`, `palette-registry.json`

## Output
`04-visual-shot-package.json`:
```json
{
  "episode_id": "ep01",
  "shot_packages": [
    {
      "shot_id": "SHOT_001",
      "camera": {},
      "lighting": "",
      "composition": "",
      "continuity": "",
      "render_constraints": "",
      "memory_images": [],
      "emotional_arc": ""
    }
  ]
}
```

## Rules
- Does NOT generate the text prompt — that's Prompt Compiler's responsibility.
- Must reference the specific `reference_image_path` from the character registry for every character in the frame.
```

- [ ] **Step 2: Rewrite `skills/prompt-compiler/SKILL.md`**

```markdown
# Skill: Prompt Compiler

## Purpose
Turns a Visual Shot Package plus registry data into a concrete prompt for the configured generator.

## Input
- `04-visual-shot-package.json`
- `registries/style-registry.json` for `generator_config` (the `generation_backend` field)

## Output
`05-prompt-package.json`:
```json
{
  "episode_id": "ep01",
  "prompt_packages": [
    {
      "shot_id": "SHOT_001",
      "prompt_text": "",
      "reference_images": [],
      "generator_globals": {},
      "compiler_flags": {}
    }
  ]
}
```

## Rules
- Resolves conflicts between registry data (e.g. if a scene's lighting contradicts the location's default lighting, the scene wins).
- Builds the prompt for the `generation_backend` in `style-registry.json` (`claude-mcp-media` by default for the pilot; `fallback_model` is a documented, inactive alternative — switching to it requires no changes to this skill, only flipping `generation_backend`).
```

- [ ] **Step 3: Rewrite `skills/image-director/SKILL.md`**

```markdown
# Skill: Image Director

## Purpose
The final quality control point before actual generation: applies the project's Style Preset, validates consistency against earlier frames of this character/location, and calls the generator.

## Input
`05-prompt-package.json`

## Output
`06-generation-log.json`:
```json
{
  "episode_id": "ep01",
  "generated_assets": [
    {
      "shot_id": "SHOT_001",
      "asset_path": "",
      "generated_at": "",
      "generator_call": "generate_image | upscale_image",
      "flagged_for_review": false
    }
  ]
}
```

## Rules
- Does NOT redesign characters or environments — only applies style and validates.
- If consistency is in question (a new frame diverges significantly from the character's reference_image), flags `flagged_for_review: true` rather than generating silently.
- Style is applied AFTER prompt compilation, never before.
- Calls the generator via the `generation_backend` in `style-registry.json` (`generate_image`/`upscale_image` for the pilot).
```

- [ ] **Step 4: Verify the required sections are present in all three files**

Run: `for f in skills/visual-shot-package/SKILL.md skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md; do c=$(grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" "$f"); echo "$f: $c"; done`
Expected: all three lines show `4`

- [ ] **Step 5: Validate all three JSON examples**

Run: `for f in skills/visual-shot-package/SKILL.md skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md; do sed -n '/```json/,/```/p' "$f" | sed '1d;$d' | python3 -m json.tool > /dev/null && echo "$f VALID"; done`
Expected:
```
skills/visual-shot-package/SKILL.md VALID
skills/prompt-compiler/SKILL.md VALID
skills/image-director/SKILL.md VALID
```

- [ ] **Step 6: Verify `generation_backend` is mentioned in prompt-compiler and image-director**

Run: `grep -l "generation_backend" skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md | wc -l`
Expected: `2`

- [ ] **Step 7: Commit**

```bash
git add skills/visual-shot-package/SKILL.md skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md
git commit -m "docs: add concrete output schemas and MCP generator binding to compilation skills"
```

---

## Task 6: New Skill — Produce Episode (Orchestrator)

**Files:**
- Create: `skills/produce-episode/SKILL.md`

**Interfaces:**
- Consumes: every file/field name from Tasks 1-5b (`00-source-extract.json` … `06-generation-log.json`, `audio/*.json`, `locked`, `flagged_for_review`)
- Produces: no new data format — just a sequence of calls and checkpoints for a human (and later OpenClaw) to read

- [ ] **Step 1: Create `skills/produce-episode/SKILL.md`**

```markdown
# Skill: Produce Episode

## Purpose
Orchestrates the full production pipeline for one episode: calls every skill agent in order, reads/writes episode files under the fixed numbering scheme, and pauses at human-confirmation checkpoints. This is the single command a human uses to run the whole process — not 8 separate commands.

## Input
- `episode_id` (e.g. `ep02`)
- `episodes/<episode_id>/script.md` — the editorial brief: source URL(s), episode scope, deliberate changes

## Sequence

1. **Source Ingestion** → writes `episodes/<episode_id>/00-source-extract.json`
   → **CHECKPOINT 0**: show `adaptation_notes` to the human, wait for confirmation that the transformation is sufficient
2. **Registry Builder** (on-demand) → creates unlocked entries for new characters/locations in `registries/*.json`
   → **CHECKPOINT 2**: show the new entries, wait for the human to set `locked:true`
3. **Master Narrative** → writes `episodes/<episode_id>/01-master-narrative.json`
   → **CHECKPOINT 1**: show the scene breakdown, wait for confirmation
4. In parallel (independent branches, may run in either order):
   - **Visual branch**: Scene Intelligence Engine → `02-scene-intelligence.json` → Storyboard Planner → `03-storyboard.json` (calls Registry Builder on-demand if new locations/props appear) → Visual Shot Package → `04-visual-shot-package.json` → Prompt Compiler → `05-prompt-package.json`
     → **CHECKPOINT 3**: show the shot list and compiled prompts, wait for confirmation before spending generation calls
     → Image Director → `06-generation-log.json` (flags `flagged_for_review` instead of silently generating)
   - **Audio branch**: Narrator/Audio Director → `audio/02b-narration-script.json` → `audio/generation-log.json` (flags `flagged_for_review` instead of silently generating)
5. **Assembly** (a mechanical script, not an LLM call) → assembles `06-generation-log.json` + `audio/generation-log.json` into `episodes/<episode_id>/final/<episode_id>.mp4`
   → **CHECKPOINT 5**: show the video, wait for a publish decision

## Rules
- Every step reads only the file(s) explicitly listed in that skill's own `Input` — it never "recalls" data from earlier conversation instead of reading the file.
- Pausing at a checkpoint means: show the human the concrete artifact (JSON/list/video) and wait, literally, for confirmation in chat before reading the next skill.
- If the human manually edits an intermediate file after a checkpoint (e.g. edits `01-master-narrative.json`), the next pipeline step reads the edited version, not the agent's original output.
- Any step can be rerun in isolation (e.g. "regenerate just `03-storyboard.json`") — that's simply calling the matching skill again with the same input file.
```

- [ ] **Step 2: Verify all 5 checkpoints are mentioned**

Run: `grep -c "CHECKPOINT" skills/produce-episode/SKILL.md`
Expected: `5`

- [ ] **Step 3: Verify every pipeline file name is present**

Run: `for name in 00-source-extract.json 01-master-narrative.json 02-scene-intelligence.json 02b-narration-script.json 03-storyboard.json 04-visual-shot-package.json 05-prompt-package.json 06-generation-log.json; do grep -q "$name" skills/produce-episode/SKILL.md || echo "MISSING: $name"; done; echo DONE`
Expected: `DONE` (with no `MISSING` lines)

- [ ] **Step 4: Commit**

```bash
git add skills/produce-episode/SKILL.md
git commit -m "feat: add Produce Episode orchestrating skill"
```

---

## Task 7: Restructure the episodes/ep01 Template Under the New Numbering

**Files:**
- Modify: `episodes/ep01/script.md` (whole file)
- Create: `episodes/ep01/00-source-extract.json`
- Create: `episodes/ep01/01-master-narrative.json`
- Create: `episodes/ep01/02-scene-intelligence.json`
- Create: `episodes/ep01/03-storyboard.json`
- Create: `episodes/ep01/04-visual-shot-package.json`
- Create: `episodes/ep01/05-prompt-package.json`
- Create: `episodes/ep01/06-generation-log.json`
- Create: `episodes/ep01/audio/02b-narration-script.json`
- Create: `episodes/ep01/audio/generation-log.json`
- Create: `episodes/ep01/final/.gitkeep`
- Delete: `episodes/ep01/shot-package.json` (replaced by `04-visual-shot-package.json`)
- Delete: `episodes/ep01/prompts.json` (replaced by `05-prompt-package.json`)

**Interfaces:**
- Consumes: every schema from Tasks 2-5b
- Produces: a working episode template, which Task 8 describes in the documentation

- [ ] **Step 1: Rewrite `episodes/ep01/script.md`**

```markdown
# Episode 01 — [Working Title]

## Source
- Chapter URL(s): [link to the source]
- Chapters this episode covers: [e.g. 1-3]

## Deliberate Changes (for Source Ingestion / Master Narrative)
- [e.g. "compress arc X into one scene"]
- [e.g. "rename character Y"]

## Notes
- Characters appearing for the first time: ...
- New locations: ...
```

- [ ] **Step 2: Create the new empty pipeline artifacts**

`episodes/ep01/00-source-extract.json`:
```json
{
  "episode_id": "ep01",
  "source_refs": [],
  "characters_extracted": [],
  "world_facts": [],
  "plot_beats": [],
  "adaptation_notes": { "renamed": [], "compressed": [], "changed": [] }
}
```

`episodes/ep01/01-master-narrative.json`:
```json
{
  "episode_id": "ep01",
  "scenes": []
}
```

`episodes/ep01/02-scene-intelligence.json`:
```json
{
  "episode_id": "ep01",
  "scenes": []
}
```

`episodes/ep01/03-storyboard.json`:
```json
{
  "episode_id": "ep01",
  "shots": []
}
```

`episodes/ep01/04-visual-shot-package.json`:
```json
{
  "episode_id": "ep01",
  "shot_packages": []
}
```

`episodes/ep01/05-prompt-package.json`:
```json
{
  "episode_id": "ep01",
  "prompt_packages": []
}
```

`episodes/ep01/06-generation-log.json`:
```json
{
  "episode_id": "ep01",
  "generated_assets": []
}
```

`episodes/ep01/audio/02b-narration-script.json`:
```json
{
  "episode_id": "ep01",
  "narration_lines": []
}
```

`episodes/ep01/audio/generation-log.json`:
```json
{
  "episode_id": "ep01",
  "generated_assets": []
}
```

- [ ] **Step 3: Create a placeholder for the empty final/ directory**

Run: `touch episodes/ep01/final/.gitkeep`

- [ ] **Step 4: Delete the obsolete files**

Run: `git rm episodes/ep01/shot-package.json episodes/ep01/prompts.json`

- [ ] **Step 5: Validate every new JSON file**

Run: `for f in episodes/ep01/00-source-extract.json episodes/ep01/01-master-narrative.json episodes/ep01/02-scene-intelligence.json episodes/ep01/03-storyboard.json episodes/ep01/04-visual-shot-package.json episodes/ep01/05-prompt-package.json episodes/ep01/06-generation-log.json episodes/ep01/audio/02b-narration-script.json episodes/ep01/audio/generation-log.json; do python3 -m json.tool "$f" > /dev/null && echo "$f VALID"; done`
Expected: all 9 files print `VALID`

- [ ] **Step 6: Verify the obsolete files are actually gone**

Run: `test -f episodes/ep01/shot-package.json && echo STILL_EXISTS || echo REMOVED; test -f episodes/ep01/prompts.json && echo STILL_EXISTS || echo REMOVED`
Expected:
```
REMOVED
REMOVED
```

- [ ] **Step 7: Commit**

```bash
git add episodes/ep01/
git commit -m "feat: restructure ep01 template to numbered pipeline artifact convention"
```

---

## Task 8: Sync docs/architecture.md and README.md

**Files:**
- Modify: `docs/architecture.md` (Pipeline, stage descriptions, Registry System, Current JSON Artifacts, Open Items sections)
- Modify: `README.md` (Structure section)

**Interfaces:**
- Consumes: the final list of skills/files from Tasks 1-7
- Produces: nothing new — this is documentation, a terminal artifact meant for a human or another LLM to read

- [ ] **Step 1: Replace the `## Pipeline` section in `docs/architecture.md`**

Find the block from `## Pipeline` through the end of the `Image Director` description (before `## Registry System`) and replace it with:

```markdown
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
Transforms one or more finished source chapters (a web novel/manhwa by URL) into structured facts without ever storing the original text verbatim. Input: chapter URL(s). Output: `00-source-extract.json`. Never stores the original text verbatim — only facts and short original phrasing.

### Master Narrative
Turns Source Ingestion's facts into a structured narrative in its own prose. Input: `00-source-extract.json` + `script.md`. Output: narrative scenes. Never defines visuals.

### Scene Intelligence Engine
Extracts: scene intent, emotional arc, chronology, continuity, entities, environment logic.

### Storyboard Planner
Breaks scenes into cinematic shots and visual beats. Determines cameras, composition goals, pacing.

### Registry Builder
Maintains immutable registries: Character, Location, Prop, Camera, Palette, Style, Generator. Acts as the Single Source of Truth. Called on demand — first right after Source Ingestion, again during Storyboard Planner.

### Visual Shot Package
Merges the storyboard with registry data into complete visual specs. Contains: camera, lighting, composition, continuity, render constraints, memory images, emotional arc. **Does not generate prompts.**

### Prompt Compiler
Takes a Visual Shot Package + Registry. Resolves conflicts, expands registry locks, builds prompts for the `generation_backend` from the style registry.

### Image Director
Takes compiled prompts. Applies the project's Style Preset, validates consistency, calls the generator (`generate_image`/`upscale_image` for the pilot). **Never redesigns characters or environments.**

### Narrator / Audio Director
Parallel audio branch. Turns Master Narrative scenes into narration/dialogue text, generates voice via `create_voice`/`generate_audio` using each character's locked voice_id. Independent of the visual branch.

### Assembly
A mechanical ffmpeg script, not an LLM agent. Assembles images per each shot's pacing_note + the audio track + subtitles into the final mp4.
```

- [ ] **Step 2: Update the `## Current JSON Artifacts` section in `docs/architecture.md`**

Replace the line `Resolved Shot Package → Visual Shot Package → Prompt Package.` with:

```markdown
`00-source-extract.json` → `01-master-narrative.json` → `02-scene-intelligence.json` (+ in parallel `audio/02b-narration-script.json`) → `03-storyboard.json` → `04-visual-shot-package.json` → `05-prompt-package.json` → `06-generation-log.json` (+ `audio/generation-log.json`) → `final/<episode_id>.mp4`. Full field contract for each file lives in the corresponding `skills/<name>/SKILL.md`, Output section.
```

- [ ] **Step 3: Update the `## Open Items` section in `docs/architecture.md`**

Replace with:

```markdown
## Open Items (move into registries once populated)

- [ ] Populate `registries/character-registry.json` for the current story (adapted from the source)
- [ ] Populate `registries/style-registry.json` (reference images, palette, line style)
- [ ] Pick a specific source (a web-novel/manhwa URL) for the first episode
```

- [ ] **Step 4: Update the structure in `README.md`**

Find the file-tree block (```` ``` memoria/ ... ```` ) and replace it with:

```markdown
```
memoria/
├── README.md                    ← this file
├── docs/
│   ├── architecture.md          ← pipeline description and principles
│   ├── business-analysis.md     ← market, copyright, technology, business model
│   ├── pilot-plan.md            ← step-by-step pilot rollout plan + OpenClaw automation plan
│   └── superpowers/
│       ├── specs/                ← architecture design specs
│       └── plans/                ← implementation plans
├── registries/                  ← Single Source of Truth: characters, locations, style, etc.
│   ├── character-registry.json
│   ├── location-registry.json
│   ├── prop-registry.json
│   ├── camera-registry.json
│   ├── palette-registry.json
│   └── style-registry.json
├── characters/                  ← character sheets (reference images + description) per character
├── skills/                      ← every pipeline agent as a SKILL.md (OpenClaw-compatible)
│   ├── source-ingestion/
│   ├── master-narrative/
│   ├── scene-intelligence-engine/
│   ├── storyboard-planner/
│   ├── registry-builder/
│   ├── visual-shot-package/
│   ├── prompt-compiler/
│   ├── image-director/
│   ├── narrator-audio-director/
│   └── produce-episode/         ← orchestrates the whole pipeline as one command
└── episodes/                    ← working files for each episode
    └── ep01/
        ├── script.md              ← editorial brief: source URL + deliberate changes
        ├── 00-source-extract.json
        ├── 01-master-narrative.json
        ├── 02-scene-intelligence.json
        ├── 03-storyboard.json
        ├── 04-visual-shot-package.json
        ├── 05-prompt-package.json
        ├── 06-generation-log.json
        ├── audio/
        └── final/
```
```

- [ ] **Step 5: Verify the new skill folders are mentioned in both files**

Run: `for name in source-ingestion narrator-audio-director produce-episode; do grep -l "$name" docs/architecture.md README.md; done`
Expected: each of the three `name` values is found in at least one of the two files (at least 3 output lines total)

- [ ] **Step 6: Commit**

```bash
git add docs/architecture.md README.md
git commit -m "docs: sync architecture.md and README.md with new pipeline stages and file layout"
```

---

## Final Repository Check

- [ ] **Step 1: Every JSON file in the repository is valid**

Run: `find registries episodes -name "*.json" -exec python3 -m json.tool {} \; > /dev/null && echo ALL_VALID`
Expected: `ALL_VALID`

- [ ] **Step 2: Every SKILL.md has the 4 required sections**

Run: `for f in skills/*/SKILL.md; do c=$(grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" "$f"); [ "$c" -lt 4 ] && echo "INCOMPLETE: $f ($c)"; done; echo CHECK_DONE`
Expected: `CHECK_DONE` with no `INCOMPLETE` lines

- [ ] **Step 3: git status is clean (everything committed)**

Run: `git status --short`
Expected: empty output
