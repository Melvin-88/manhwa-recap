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
- Must reference the specific `reference_sheet_path` from the character registry for every character in the frame.
