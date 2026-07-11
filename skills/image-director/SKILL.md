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
      "asset_path": "",
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
- Стиль застосовується ПІСЛЯ компіляції промпту, ніколи до.
- Викликає генератор через `generation_backend` зі `style-registry.json` (`generate_image`/`upscale_image` для пілоту).
