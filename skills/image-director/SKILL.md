# Skill: Image Director

## Purpose
The final control point before actual generation: applies the project's Style Preset, validates consistency against earlier frames of this character/location, and calls the generator.

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
      "asset_path": "episodes/<episode_id>/generated/SHOT_001.png",
      "generated_at": "",
      "generator_call": "generate_image | upscale_image",
      "flagged_for_review": false
    }
  ]
}
```

## Rules
- Does NOT redesign characters or environments — only applies style and generates.
- Does NOT render its own verdict on image quality/consistency — writes `flagged_for_review: false` by default for a just-generated frame; the final value of this field belongs exclusively to the Image QA skill, which runs immediately afterward.
- Style is applied AFTER prompt compilation, never before: Image Director takes `prompt_text` from Prompt Compiler and **appends** a text description of style from `project_style` (`art_style` + `line_weight` + `shading_approach`) in `style-registry.json` — this combined text is what goes into the generator call.
- For `generation_backend: "claude-mcp-media"` there is no separate "style" API — style exists only as text inside the prompt. Never call the generator with a prompt that doesn't include the style string from `style-registry.json`.
- Chooses the specific generator model based on shot type: if the shot contains at least one registered character (`characters_in_frame` is non-empty), use the `character_reference_model` from `style-registry.json` and **always pass its `reference_sheet_path` as `medias` (role: image)**; if the shot has no characters at all, the `no_character_model` may be used instead. Never use a model that ignores the supplied text prompt (one such model was found to return a random invented character instead of the prompt's description — do not use it).
- **Selects the correct character-reference version for the current scene.** A character may have multiple entries in `appearance_states` (see Registry Builder) — Image Director picks the entry whose `valid_from_scene` is the latest one that has already occurred at or before the current shot's `scene_id`. Never uses a stale version (e.g. a character's starting outfit in a shot that takes place after an outfit change), and never uses a version "from the future" relative to the current scene.
- If the shot contains a registered recurring creature (`creature_id` with `recurring: true` in `creature-registry.json`) or an item with a populated `reference_image_path` in `prop-registry.json`, passes their reference the same way via `medias` (role: image), in addition to characters.
- If a character doesn't yet have a populated `reference_sheet_path` in `character-registry.json`, Image Director first generates its reference sheet (see the Registry Builder rule), and only then generates the shot containing that character.
- Calls the generator via the `generation_backend` in `style-registry.json` (`generate_image`/`upscale_image` for the pilot).
- **The generator's result always arrives as a temporary URL on a third-party CDN — it can never be stored as-is.** Image Director downloads the actual file into `stories/<story_slug>/episodes/<episode_id>/generated/<shot_id>.png` (a character reference sheet goes to `stories/<story_slug>/characters/CHAR_NNN/reference.png`) and records a local relative path in `asset_path`/`reference_sheet_path`, never a URL.
