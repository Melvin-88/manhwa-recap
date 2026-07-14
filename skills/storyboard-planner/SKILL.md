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
- **Detects recurring non-human creatures/objects.** If the same creature (per its description) appears in ≥2 shots, calls Registry Builder to register it in `creature-registry.json` with `recurring: true` (a reference sheet is generated only for these, not for one-off background monsters). Likewise for visually distinctive objects that recur across multiple shots (a weapon, a unique artifact) — registers a `reference_image_path` in `prop-registry.json`.
