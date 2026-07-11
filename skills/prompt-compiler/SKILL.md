# Skill: Prompt Compiler

## Purpose
Перетворює Visual Shot Package + дані реєстру в конкретний промпт для обраного генератора.

## Input
- `04-visual-shot-package.json`
- `registries/style-registry.json` для `generator_config` (поле `generation_backend`)

## Output
`05-prompt-package.json`:
```json
{
  "episode_id": "ep01",
  "prompt_packages": [
    {
      "shot_id": "SHOT_001",
      "prompt_text": "",
      "reference_images": [],
      "generator_globals": {},
      "compiler_flags": {}
    }
  ]
}
```

## Rules
- Вирішує конфлікти між registry-даними (напр. якщо освітлення сцени суперечить дефолтному освітленню локації — сцена має пріоритет).
- Будує промпт під `generation_backend` зі `style-registry.json` (`claude-mcp-media` за замовчуванням для пілоту; `fallback_model` — задокументована, неактивна альтернатива, перехід на яку не вимагає змін цього skill, лише перемикання `generation_backend`).
