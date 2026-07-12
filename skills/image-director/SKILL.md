# Skill: Image Director

## Purpose
Фінальний контроль якості перед власне генерацією: застосовує Style Preset проєкту, валідує консистентність із попередніми кадрами цього персонажа/локації, викликає генератор.

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
- НЕ перепроєктовує персонажів чи середовища — лише застосовує стиль і валідує.
- Якщо консистентність під питанням (новий кадр суттєво відрізняється від reference_image персонажа) — позначає `flagged_for_review: true`, не генерує мовчки.
- Стиль застосовується ПІСЛЯ компіляції промпту, ніколи до: Image Director бере `prompt_text` з Prompt Compiler і **дописує до нього** текстовий опис стилю з `project_style` (`art_style` + `line_weight` + `shading_approach`) зі `style-registry.json` — саме цей об'єднаний текст іде у виклик генератора.
- Для `generation_backend: "claude-mcp-media"` немає окремого API для "стилю" — стиль існує лише як текст у промпті. Ніколи не викликати генератор з промптом, що не містить рядка стилю з `style-registry.json`.
- Обирає конкретну модель генератора під тип кадру: якщо в кадрі є хоча б один зареєстрований персонаж (`characters_in_frame` непорожній) — використовує `character_reference_model` зі `style-registry.json` (`nano_banana_pro`) і **обов'язково передає його `reference_sheet_path` як `medias` (role: image)**; якщо в кадрі немає жодного персонажа — можна використати `no_character_model` (`z_image`). Ніколи не використовувати модель, що ігнорує наданий текстовий промпт (виявлено на моделі `soul_cast` — вона повертає випадковий вигаданий персонаж замість опису з промпту; не використовувати).
- **Обирає правильну версію референсу персонажа під поточну сцену.** Персонаж може мати кілька записів у `appearance_states` (див. Registry Builder) — Image Director бере той запис, чий `valid_from_scene` є останнім (найпізнішим), що ще настав до або включно з `scene_id` поточного шоту. Ніколи не використовує застарілу версію (напр. стартовий одяг персонажа в кадрі, що відбувається вже після зміни вбрання) і ніколи не використовує версію "з майбутнього" відносно поточної сцени.
- Якщо в кадрі є зареєстрована повторювана істота (`creature_id` з `recurring: true` в `creature-registry.json`) або предмет із заповненим `reference_image_path` в `prop-registry.json` — передає їх референс так само через `medias` (role: image), додатково до персонажів.
- Якщо персонаж ще не має заповненого `reference_sheet_path` у `character-registry.json` — Image Director спершу генерує його референс-аркуш (див. правило Registry Builder), а вже потім кадр із цим персонажем.
- Викликає генератор через `generation_backend` зі `style-registry.json` (`generate_image`/`upscale_image` для пілоту).
- **Результат генератора завжди приходить як тимчасовий URL стороннього CDN — його не можна зберігати як є.** Image Director завантажує фактичний файл у `stories/<story_slug>/episodes/<episode_id>/generated/<shot_id>.png` (референс-аркуш персонажа — у `stories/<story_slug>/characters/CHAR_NNN/reference.png`) і записує в `asset_path`/`reference_sheet_path` локальний відносний шлях, не URL.
