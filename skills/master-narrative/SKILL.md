# Skill: Master Narrative

## Purpose
Перетворює структуровані факти від Source Ingestion у структурований наратив власною прозою. Джерело істини для всіх наступних етапів пайплайну. Момент трансформації/стиснення історії — не Source Ingestion.

## Input
`00-source-extract.json` від Source Ingestion (факти: персонажі, world_facts, plot_beats, adaptation_notes) + `script.md` (редакційний бриф людини: обсяг епізоду, свідомі зміни)

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
- Ніколи не визначає візуал (це відповідальність Storyboard Planner/Visual Shot Package).
- Пише власну прозу на основі фактів з `00-source-extract.json` — не перефразовує оригінальний текст джерела, бо його в файлі й немає (лише факти).
- Кожна сцена — окрема одиниця, придатна для подальшої обробки Scene Intelligence Engine.

## Example invocation (концептуально)
"Ось факти з 00-source-extract.json для епізоду 1: [JSON]. Побудуй Master Narrative у форматі 01-master-narrative.json зі сценами."
