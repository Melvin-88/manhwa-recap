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
Source Ingestion
   ↓
   ├──→ Registry Builder (on-demand)
   ↓
Master Narrative
   ↓
   ├─── Візуальна гілка ────────────────────────┐
   │  Scene Intelligence Engine                 │
   │     ↓                                      │
   │  Storyboard Planner ←── Registry Builder    │
   │     ↓                                      │
   │  Visual Shot Package                       │
   │     ↓                                      │
   │  Prompt Compiler                           │
   │     ↓                                      │
   │  Image Director → generate_image (MCP)     │
   │                                             │
   └─── Аудіо гілка ────────────────────────────┐│
      Narrator / Audio Director                 ││
        ↓                                       ││
      create_voice + generate_audio (MCP)       ││
                                                  ↓↓
                                              Assembly
                                       (механічний ffmpeg-скрипт,
                                        не LLM-агент)
```

### Source Ingestion
Перетворює готовий розділ(и) джерела (веб-новела/манхва за URL) у структуровані факти без збереження оригінального тексту дослівно. Вхід: URL(и) розділів. Вихід: `00-source-extract.json`. Ніколи не зберігає оригінальний текст дослівно — лише факти й короткі власні формулювання.

### Master Narrative
Перетворює факти від Source Ingestion в структурований наратив власною прозою. Вхід: `00-source-extract.json` + `script.md`. Вихід: наративні сцени. Ніколи не визначає візуал.

### Scene Intelligence Engine
Виділяє: намір сцени, емоційну арку, хронологію, безперервність, сутності, логіку середовища.

### Storyboard Planner
Розбиває сцени на кінематографічні шоти й візуальні біти. Визначає камери, композиційні цілі, темп.

### Registry Builder
Підтримує незмінні реєстри: Character, Location, Prop, Camera, Palette, Style. Діє як Single Source of Truth. Викликається на вимогу — вперше одразу після Source Ingestion, повторно під час Storyboard Planner.

### Visual Shot Package
Об'єднує storyboard з інформацією реєстру в повні візуальні специфікації. Містить: камеру, освітлення, композицію, безперервність, обмеження рендеру, memory images, емоційну арку. **Не генерує промпти.**

### Prompt Compiler
Приймає Visual Shot Package + Registry. Вирішує конфлікти, розгортає registry locks, будує промпти під `generation_backend` зі style-registry.

### Image Director
Приймає скомпільовані промпти. Застосовує Style Preset проєкту, валідує консистентність, викликає генератор (`generate_image`/`upscale_image` для пілоту). **Не перепроєктовує персонажів чи середовища.**

### Narrator / Audio Director
Паралельна аудіо-гілка. Перетворює сцени Master Narrative у наративний/діалоговий текст, генерує озвучення через `create_voice`/`generate_audio`, використовуючи закріплені voice_id персонажів. Не залежить від візуальної гілки.

### Assembly
Механічний ffmpeg-скрипт, не LLM-агент. Збирає картинки за pacing_note шотів + аудіодоріжку + субтитри у фінальний mp4.

## Registry System

| Реєстр | Призначення |
|---|---|
| CHAR | Канонічні визначення персонажів (зовнішність, character sheet, voice_id) |
| LOC | Локації та їхні візуальні характеристики |
| PROP | Повторювані предмети/об'єкти |
| CAM | Пресети камер (кут, лінза, рух) |
| PAL | Кольорові палітри по сценах/настроях |
| STYLE | Глобальний стиль проєкту |

## Current JSON Artifacts

`00-source-extract.json` → `01-master-narrative.json` → `02-scene-intelligence.json` (+ паралельно `audio/02b-narration-script.json`) → `03-storyboard.json` → `04-visual-shot-package.json` → `05-prompt-package.json` → `06-generation-log.json` (+ `audio/generation-log.json`) → `final/<episode_id>.mp4`. Повний контракт полів кожного файлу — у відповідному `skills/<name>/SKILL.md`, секція Output.

## Design Decisions

- Кожен агент має рівно одну відповідальність.
- Реєстри незмінні (immutable) в межах одного епізоду.
- Генерація промптів відокремлена від візуального планування.
- Стиль застосовується ПІСЛЯ компіляції промпту, не до.

## Future Expansion

Prompt Optimizer, Continuity Resolver, Animation, Video, 3D support.

## Open Items (перенести в реєстри при заповненні)

- [ ] Наповнити `registries/character-registry.json` для поточної історії (адаптованої з джерела)
- [ ] Наповнити `registries/style-registry.json` (референс-зображення, палітра, лінія)
- [ ] Обрати конкретне джерело (URL веб-новели/манхви) для першого епізоду
