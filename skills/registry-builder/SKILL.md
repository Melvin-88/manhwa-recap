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
  "reference_sheet_path": "characters/CHAR_002/reference_v1.png",
  "appearance_states": [
    {
      "state_id": "v1",
      "description": "базовий вигляд / стартове вбрання",
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
- Ніколи не змінює існуючий `locked:true` запис без явного підтвердження людини.
- **Нові персонажі отримують reference-аркуш ДО того, як з'являються в будь-якому сюжетному кадрі.** Registry Builder викликає Image Director окремо, щоб згенерувати 1 канонічне референс-зображення персонажа (модель `character_reference_model` зі `style-registry.json`, наразі `nano_banana_pro`) на основі полів `appearance`. Image Director завантажує фактичний файл у `characters/CHAR_NNN/reference_vN.png` (у фолдері історії, не тимчасовий URL) — саме цей локальний шлях записується і в `appearance_states[].reference_sheet_path`, і (для поточної/останньої версії) в топлевельний `reference_sheet_path`. Лише після цього персонажа можна `locked:true`, і лише після цього Storyboard/Prompt Compiler можуть використовувати цього персонажа в кадрах.
- **Референс-аркуш — це "розворот" персонажа, не один портрет анфас.** Одне зображення має містити кілька ракурсів (анфас, 3/4, профіль; за потреби — спина) і 2-3 вирази обличчя в межах одного канонічного вбрання. Причина: генератор, побачивши персонажа лише спереду, вигадує довільні деталі (напр. хвостик волосся), коли кадр вимагає виду збоку/ззаду — розворот усуває цю плутанину. Орієнтир якості — вже згенерований `characters/CHAR_003/reference.png`.
- **Версії вигляду (`appearance_states`):** коли сюжет незворотно змінює вигляд персонажа (новий одяг, нова зброя, поранення, трансформація) — а не тимчасова деталь одного кадру — Registry Builder додає новий запис в `appearance_states` з новим `state_id`, `valid_from_scene` (перша сцена, де діє ця зміна) і власним референс-аркушем (той самий формат розвороту, той самий базовий вигляд обличчя/раси персонажа, оновлене вбрання/деталі). Сигнал для нової версії — поле `continuity_requirements` у `02-scene-intelligence.json`, коли там зазначено "з цієї сцени і надалі..." (напр. зміна одягу після втечі з шахти). Стара версія лишається в масиві (не видаляється) — вона потрібна для кадрів із попередніх сцен.
- Кожен реєстр — окремий файл, не змішувати типи сутностей в одному файлі.
- Записи персонажів, створені з Source Ingestion, обов'язково заповнюють `source_name` для трасування адаптації (ніколи не виводиться в публічний контент).
- `adapted_name` від Source Ingestion стає полем `name` у реєстрі; `source_name` копіюється як є.

## Creature Registry (`registries/creature-registry.json`)
Окремий реєстр для нелюдських істот/монстрів, що не є персонажами (не мають `voice_id`, не ведуть діалогів), але з'являються в кадрах.
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
- **Референс-аркуш генерується ЛИШЕ якщо `recurring: true`** — істота з'являється в ≥2 шотах сторіборду. Одноразовий фоновий монстр (`recurring: false`) референсу не потребує — генерується довільно щоразу, це не впливає на консистентність, бо повторного кадру з ним не буде.
- `recurring` визначається під час Storyboard Planner: якщо однакова істота (за описом сцени) фігурує в кількох `shot_id`, Storyboard Planner викликає Registry Builder для реєстрації/позначення `recurring: true`.
- Формат референс-аркуша — той самий "розворот" (кілька ракурсів), що й для персонажів.

## Reference-зображення для предметів (`registries/prop-registry.json`)
- Поле `reference_image_path` (опційне) заповнюється так само, лише якщо предмет: (а) з'являється в ≥2 шотах, і (б) достатньо візуально своєрідний, щоб плутанина між кадрами була б помітною (зброя, унікальний артефакт). Типовий фоновий реквізит референсу не потребує.
