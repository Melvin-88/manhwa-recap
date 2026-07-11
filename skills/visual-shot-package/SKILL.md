# Skill: Visual Shot Package

## Purpose
Об'єднує storyboard-шот з даними реєстру в повну візуальну специфікацію, готову для компіляції промпту.

## Input
- Шот з `03-storyboard.json`
- Відповідні записи з `registries/character-registry.json`, `location-registry.json`, `prop-registry.json`, `camera-registry.json`, `palette-registry.json`

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
- НЕ генерує текстовий промпт — це відповідальність Prompt Compiler.
- Обов'язково посилається на конкретні `reference_sheet_path` з character-registry для кожного персонажа в кадрі.
