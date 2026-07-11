# Skill: Prompt Compiler

## Purpose
Перетворює Visual Shot Package + дані реєстру в конкретний промпт для обраної генеративної моделі.

## Input
- Visual Shot Package (JSON)
- Style registry (registries/style-registry.json) для generator_config

## Output
Model-specific промпт-пакет:
- prompt_text (готовий текстовий промпт)
- reference_images (шляхи до character sheets, якщо модель підтримує image-conditioning — Nano Banana 2, Seedream)
- generator_globals (негативні промпти, seed-стратегія якщо застосовно)
- compiler_flags

## Rules
- Вирішує конфлікти між registry-даними (напр. якщо освітлення сцени суперечить дефолтному освітленню локації — сцена має пріоритет).
- Будує промпт під конкретну модель з generator_config (nano-banana-2 / seedream-4.5 / fallback sdxl-flux-lora) — формат промпту відрізняється між ними.
