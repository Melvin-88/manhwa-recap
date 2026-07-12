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
Перетворює джерело (веб-новела/манхва) у структуровані факти без збереження оригінального тексту дослівно. Працює на рівні всього твору: факти накопичуються батчами розділів (погодженими з людиною) у `source-material/master-extract.json` (у межах фолдера конкретної історії — див. "Структура для кількох історій"), а не наново для кожного епізоду. Прогалини (наприклад, ще неописана зовнішність персонажа) заповнюються автоматично й позначаються як `auto_generated_fields`, без зупинки на кожному питанні — підсумок іде на підтвердження людині після завершення батчу. Епізодний `00-source-extract.json` — це зріз (`beat_range`) з `master-extract.json`, не окремий прогін ingestion. Ніколи не зберігає оригінальний текст дослівно — лише факти й короткі власні формулювання.

### Master Narrative
Перетворює факти від Source Ingestion в структурований наратив власною прозою. Вхід: `00-source-extract.json` + `script.md`. Вихід: наративні сцени. Ніколи не визначає візуал.

### Scene Intelligence Engine
Виділяє: намір сцени, емоційну арку, хронологію, безперервність, сутності, логіку середовища.

### Storyboard Planner
Розбиває сцени на кінематографічні шоти й візуальні біти. Визначає камери, композиційні цілі, темп.

### Registry Builder
Підтримує незмінні реєстри: Character, Location, Prop, Camera, Palette, Style. Діє як Single Source of Truth. Викликається на вимогу — вперше одразу після Source Ingestion, повторно під час Storyboard Planner. Новий персонаж отримує референс-аркуш (згенерований Image Director) ДО того, як зможе з'явитись у сюжетному кадрі, і лише після цього — `locked:true`.

### Visual Shot Package
Об'єднує storyboard з інформацією реєстру в повні візуальні специфікації. Містить: камеру, освітлення, композицію, безперервність, обмеження рендеру, memory images, емоційну арку. **Не генерує промпти.**

### Prompt Compiler
Приймає Visual Shot Package + Registry. Вирішує конфлікти, розгортає registry locks, будує промпти під `generation_backend` зі style-registry.

### Image Director
Приймає скомпільовані промпти. Застосовує Style Preset проєкту, валідує консистентність, викликає генератор (`generate_image`/`upscale_image` для пілоту). **Не перепроєктовує персонажів чи середовища.** Кадри з зареєстрованим персонажем завжди передають його `reference_sheet_path` як reference-зображення генератору (модель `character_reference_model` зі `style-registry.json`) для консистентності обличчя/дизайну між кадрами; кадри без персонажів можуть використовувати простішу модель без reference-входу.

### Narrator / Audio Director
Паралельна аудіо-гілка. Перетворює сцени Master Narrative у наративний/діалоговий текст, генерує озвучення через `create_voice`/`generate_audio`, використовуючи закріплені voice_id персонажів. Не залежить від візуальної гілки.

### Assembly
Механічний ffmpeg-скрипт, не LLM-агент. Збирає картинки за pacing_note шотів + аудіодоріжку + субтитри у фінальний mp4.

## Registry System

| Реєстр | Призначення |
|---|---|
| CHAR | Канонічні визначення персонажів (зовнішність, character sheet, voice_id) |
| CRE | Повторювані нелюдські істоти/монстри (без діалогів/voice_id), референс лише для `recurring: true` |
| LOC | Локації та їхні візуальні характеристики |
| PROP | Повторювані предмети/об'єкти, опційний `reference_image_path` для візуально своєрідних |
| CAM | Пресети камер (кут, лінза, рух) |
| PAL | Кольорові палітри по сценах/настроях |
| STYLE | Глобальний стиль проєкту |

### Референс-аркуші: розворот, не портрет

Референс-зображення персонажа (і повторюваної істоти) — це один "розворот"-аркуш із кількома ракурсами (анфас, 3/4, профіль, за потреби спина) і 2-3 виразами обличчя в межах одного вбрання, а не єдиний портрет анфас. Причина: генератор, маючи лише вигляд спереду, вигадує довільні деталі для кадрів із виду збоку/ззаду (напр. хвостик волосся, якого немає на референсі) — розворот усуває цю невідповідність. Орієнтир якості — `characters/CHAR_003/reference.png`.

### Версії вигляду персонажа (`appearance_states`)

Коли сюжет незворотно змінює вигляд персонажа (нове вбрання, нова зброя, поранення, трансформація), Registry Builder додає новий запис в `appearance_states[]` цього персонажа з власним референс-аркушем і `valid_from_scene`. Image Director при генерації кадру обирає версію, чий `valid_from_scene` є найпізнішим з тих, що вже настали для сцени поточного шоту — ніколи не застарілу й ніколи не з майбутнього. Стара версія лишається в масиві (потрібна для кадрів із попередніх сцен). Повний контракт полів — `skills/registry-builder/SKILL.md`.

## Current JSON Artifacts

`00-source-extract.json` → `01-master-narrative.json` → `02-scene-intelligence.json` (+ паралельно `audio/02b-narration-script.json`) → `03-storyboard.json` → `04-visual-shot-package.json` → `05-prompt-package.json` → `06-generation-log.json` (+ `audio/generation-log.json`) → `final/<episode_id>.mp4`. Повний контракт полів кожного файлу — у відповідному `skills/<name>/SKILL.md`, секція Output.

## Структура для кількох історій

`skills/` і сам пайплайн — story-agnostic (спільні для будь-якої історії). Але дані конкретної історії (реєстри, епізоди, референс-зображення персонажів, факти з джерела) прив'язані до однієї конкретної адаптації і не повинні змішуватись між різними історіями. Тому кожна історія отримує власний ізольований фолдер:

```
stories/<story-slug>/           ← напр. stories/the-greatest-heretic/
├── source-material/
│   └── master-extract.json     ← накопичені факти з джерела (Source Ingestion)
├── registries/                 ← Character/Location/Prop/Camera/Palette/Style — ЛИШЕ цієї історії
├── characters/
│   └── CHAR_NNN/
│       └── reference.png        ← фактичний файл референс-аркуша (не URL!)
└── episodes/
    └── epNN/
        ├── script.md
        ├── 00-...06-....json     ← артефакти пайплайну
        ├── generated/            ← фактичні файли згенерованих кадрів епізоду
        ├── audio/
        └── final/
```

**Чому файли, а не URL:** зображення/аудіо, що повертає `generate_image`/`generate_audio` (MCP), спершу приходять як тимчасові URL на CDN стороннього сервісу. Ці посилання можуть протухнути чи стати недоступними. Тому Image Director (і Narrator/Audio Director) **завжди завантажують фактичний файл** у відповідну папку історії (`characters/CHAR_NNN/reference.png`, `episodes/epNN/generated/SHOT_NNN.png`) і в реєстри/логи записують **локальний відносний шлях**, а не тимчасовий URL.

**Створення нової історії:** скопіювати цю структуру з новим `<story-slug>`, запустити Source Ingestion на новому джерелі — `skills/` і `docs/` лишаються спільними, нічого в них змінювати не треба.

## Design Decisions

- Кожен агент має рівно одну відповідальність.
- Реєстри незмінні (immutable) в межах одного епізоду.
- Генерація промптів відокремлена від візуального планування.
- Стиль застосовується ПІСЛЯ компіляції промпту, не до.

## Future Expansion

Prompt Optimizer, Continuity Resolver, Animation, Video, 3D support.

## Open Items

- [x] Обрано перше джерело (URL веб-новели) і історія `the-greatest-heretic` в роботі — див. `stories/the-greatest-heretic/`
- [x] `registries/character-registry.json` наповнено для епізоду 1 (6 персонажів, референс-аркуші згенеровано)
- [x] `registries/style-registry.json` наповнено (кольорова манхва/webtoon, `character_reference_model`/`no_character_model`)
- [ ] Прогнати решту 48 шотів епізоду 1 через Visual Shot Package → Prompt Compiler → Image Director
- [ ] Narrator/Audio Director ще не запускався для жодного епізоду
