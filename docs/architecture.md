# Memoria — Architecture & Agent Specification v1.0

> Перенесено з `Memoria_AI_Pipeline_Architecture_Agent_Specification_v1.docx`. Джерело істини для цього документа — цей файл; docx більше не редагувати.

## Purpose

Цей документ визначає поточну архітектуру виробничого пайплайну Memoria AI: відповідальність кожного агента, потік даних, реєстри та принципи дизайну. Призначений як основна специфікація для онбордингу іншого AI-агента.

## Project Vision

Memoria — registry-driven cinematic image generation pipeline. Наратив є джерелом істини. Кожен етап трансформує структуровану інформацію, не вигадуючи відсутні факти.

## Core Principles

- **Narrative First** — сюжет визначає все, візуал підпорядкований йому
- **Single Source of Truth (Registry)** — персонажі/локації/стиль визначені один раз і переговорюються
- **Registry-driven workflow** — кожен етап читає з реєстрів, не вигадує на льоту
- **No hallucinations** — жоден агент не додає фактів, яких немає в наративі
- **Visual continuity** — персонаж/локація виглядають однаково між кадрами
- **Separation of responsibilities** — кожен агент має рівно одну відповідальність

## Pipeline

```
Master Narrative
   ↓
Scene Intelligence Engine
   ↓
Storyboard Planner
   ↓
Registry Builder
   ↓
Visual Shot Package
   ↓
Prompt Compiler
   ↓
Image Director
   ↓
Image Generator
```

### Master Narrative
Перетворює історію в структурований наратив. Вхід: сценарій. Вихід: наративні сцени. Ніколи не визначає візуал.

### Scene Intelligence Engine
Виділяє: намір сцени, емоційну арку, хронологію, безперервність, сутності, логіку середовища.

### Storyboard Planner
Розбиває сцени на кінематографічні шоти й візуальні біти. Визначає камери, композиційні цілі, темп.

### Registry Builder
Підтримує незмінні реєстри: Character, Location, Prop, Camera, Palette, Style, Generator. Діє як Single Source of Truth.

### Visual Shot Package
Об'єднує storyboard з інформацією реєстру в повні візуальні специфікації. Містить: камеру, освітлення, композицію, безперервність, обмеження рендеру, memory images, емоційну арку. **Не генерує промпти.**

### Prompt Compiler
Приймає Visual Shot Package + Registry. Вирішує конфлікти, розгортає registry locks, будує model-specific промпти, generator globals, compiler flags.

> **Оновлення 2026:** цільові генератори — Nano Banana 2/Pro та Seedream 4.5 (reference-native, не потребують LoRA-тренування). SDXL/Flux+LoRA лишається fallback-опцією. Prompt Compiler повинен вміти будувати промпти під обидва типи моделей.

### Image Director
Приймає скомпільовані промпти. Застосовує Style Preset проєкту, валідує консистентність, виконує model tuning, готує фінальний generation prompt. **Не перепроєктовує персонажів чи середовища.**

## Registry System

| Реєстр | Призначення |
|---|---|
| CHAR | Канонічні визначення персонажів (зовнішність, character sheet, voice_id) |
| LOC | Локації та їхні візуальні характеристики |
| PROP | Повторювані предмети/об'єкти |
| CAM | Пресети камер (кут, лінза, рух) |
| PAL | Кольорові палітри по сценах/настроях |
| STYLE | Глобальний стиль проєкту |
| GENERATOR | Налаштування конкретної генеративної моделі |

## Current JSON Artifacts

Resolved Shot Package → Visual Shot Package → Prompt Package.

## Design Decisions

- Кожен агент має рівно одну відповідальність.
- Реєстри незмінні (immutable) в межах одного епізоду.
- Генерація промптів відокремлена від візуального планування.
- Стиль застосовується ПІСЛЯ компіляції промпту, не до.

## Future Expansion

Prompt Optimizer, Continuity Resolver, Animation, Video, Audio, 3D support.

## Open Items (перенести в реєстри при заповненні)

- [ ] Наповнити `registries/character-registry.json` для поточної історії
- [ ] Наповнити `registries/style-registry.json` (референс-画像, палітра, лінія)
- [ ] Визначити конкретний Generator registry entry для Nano Banana 2 / Seedream 4.5
