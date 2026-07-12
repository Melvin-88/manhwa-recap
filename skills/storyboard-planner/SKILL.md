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
- **Виявляє повторювані нелюдські істоти/предмети.** Якщо та сама істота (за описом) фігурує в ≥2 шотах — викликає Registry Builder, щоб зареєструвати її в `creature-registry.json` з `recurring: true` (референс-аркуш генерується лише для таких, не для одноразових фонових монстрів). Так само для візуально своєрідних предметів, що повторюються в кількох шотах (зброя, унікальний артефакт) — реєструє `reference_image_path` у `prop-registry.json`.
