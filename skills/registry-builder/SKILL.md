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
  "reference_sheet_path": "characters/CHAR_002/reference_v1.png",
  "appearance_states": [
    {
      "state_id": "v1",
      "description": "base appearance / starting outfit",
      "valid_from_scene": "SCENE_001",
      "reference_sheet_path": "characters/CHAR_002/reference_v1.png",
      "locked": false
    }
  ],
  "generator_notes": { "preferred_model": "claude-mcp-media", "reference_image_count": 5, "consistency_notes": "" },
  "locked": false
}
```

## Rules
- Never modifies an existing `locked:true` entry without explicit human confirmation.
- **New characters get a reference sheet BEFORE they appear in any story shot.** Registry Builder calls Image Director separately to generate 1 canonical character reference image (the `character_reference_model` from `style-registry.json`) based on the `appearance` fields. Image Director downloads the actual file to `characters/CHAR_NNN/reference_vN.png` (inside the story's folder, never a temporary URL) — this local path is what gets recorded both in `appearance_states[].reference_sheet_path` and, for the current/latest version, in the top-level `reference_sheet_path`. Only after this can the character be set `locked:true`, and only then can Storyboard/Prompt Compiler use this character in shots.
- **A reference sheet is a character "turnaround," never a single front-facing portrait.** One image must contain several angles (front, 3/4, profile; back if needed) and 2-3 facial expressions within one canonical outfit. Rationale: given only a front view, the generator invents arbitrary details (e.g. a ponytail) whenever a shot calls for a side/back view — a turnaround removes that ambiguity.
- **Appearance versions (`appearance_states`):** when the story irreversibly changes a character's appearance (new clothing, a new weapon, an injury, a transformation) — as opposed to a one-shot temporary detail — Registry Builder adds a new entry to `appearance_states` with a new `state_id`, `valid_from_scene` (the first scene where the change applies), and its own reference sheet (same turnaround format, same underlying face/build, updated outfit/detail). The signal for a new version is the `continuity_requirements` field in `02-scene-intelligence.json` whenever it states something like "from this scene onward..." (e.g. a clothing change after an escape). The old version stays in the array (never deleted) — it's still needed for shots from earlier scenes.
- Each registry is its own file — never mix entity types in one file.
- Character entries created from Source Ingestion must populate `source_name` for adaptation traceability (never surfaced in public-facing content).
- Source Ingestion's `adapted_name` becomes the registry's `name` field; `source_name` is copied as-is.

## Creature Registry (`registries/creature-registry.json`)
A separate registry for non-human creatures/monsters that aren't characters (no `voice_id`, no dialogue) but appear in shots.
```json
{
  "creatures": [
    {
      "creature_id": "CRE_001",
      "name": "",
      "description": "",
      "recurring": false,
      "first_appearance_shot": "SHOT_040",
      "reference_sheet_path": "",
      "locked": false
    }
  ]
}
```
- **A reference sheet is generated ONLY if `recurring: true`** — the creature appears in ≥2 storyboard shots. A one-off background monster (`recurring: false`) needs no reference — it's generated freely each time, since there's no repeat appearance for consistency to matter.
- `recurring` is determined during Storyboard Planner: if the same creature (per the scene description) shows up across multiple `shot_id`s, Storyboard Planner calls Registry Builder to register it / flag it `recurring: true`.
- The reference-sheet format is the same "turnaround" (multiple angles) used for characters.

## Reference Images for Props (`registries/prop-registry.json`)
- The (optional) `reference_image_path` field is populated the same way, only when the prop: (a) appears in ≥2 shots, and (b) is visually distinctive enough that cross-shot inconsistency would be noticeable (a weapon, a unique artifact). Typical background props need no reference.
