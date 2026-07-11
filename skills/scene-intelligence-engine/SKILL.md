# Skill: Scene Intelligence Engine

## Purpose
Аналізує кожну сцену з Master Narrative і витягує глибші структурні дані, потрібні для storyboard.

## Input
Одна сцена з `01-master-narrative.json`

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
- Спирається лише на дані з Master Narrative та реєстрів, нічого не вигадує.
- Не визначає композицію кадру (це Storyboard Planner).
