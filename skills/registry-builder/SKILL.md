# Skill: Registry Builder

## Purpose
Підтримує та оновлює незмінні (у межах епізоду) реєстри: Character, Location, Prop, Camera, Palette, Style. Єдине джерело істини для всіх візуальних сутностей проєкту.

## Input
Запит на створення/оновлення запису в одному з реєстрів `registries/*.json`. Викликається на вимогу (не послідовний етап): вперше одразу після Source Ingestion (нові персонажи з `source_name`/`adapted_name`), повторно під час Storyboard Planner, якщо з'являються нові локації/пропси.

## Output
Оновлений відповідний JSON-файл реєстру. Приклад для нового персонажа з Source Ingestion:
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
- Ніколи не змінює існуючий `locked:true` запис без явного підтвердження людини.
- Нові персонажі/локації отримують character sheet / reference image перед тим, як `locked:true`.
- Кожен реєстр — окремий файл, не змішувати типи сутностей в одному файлі.
- Записи персонажів, створені з Source Ingestion, обов'язково заповнюють `source_name` для трасування адаптації (ніколи не виводиться в публічний контент).
- `adapted_name` від Source Ingestion стає полем `name` у реєстрі; `source_name` копіюється як є.
