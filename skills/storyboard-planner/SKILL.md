# Skill: Storyboard Planner

## Purpose
Розбиває сцену (вже збагачену Scene Intelligence Engine) на конкретні кінематографічні шоти.

## Input
Збагачена сцена з `02-scene-intelligence.json`

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
- Кожен шот має чітку композиційну ціль, не просто "показати сцену".
- Використовує тільки `camera_id` з `registries/camera-registry.json`, не вигадує нові пресети на льоту (при потребі — викликає Registry Builder).
