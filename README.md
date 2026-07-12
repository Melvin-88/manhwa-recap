# Memoria — AI Content Pipeline

Registry-driven pipeline для генерації озвучених серій з AI-згенерованими зображеннями (формат "аудіокнига з картинками").

## Навіщо ця структура

Все в цьому репозиторії — звичайний Markdown/JSON. Жодних форматів, специфічних для однієї LLM. Це означає:
- Будь-яка LLM (Claude, GPT, Gemini, локальна модель) може прочитати весь контекст проєкту, просто відкривши файли.
- Структура `skills/<name>/SKILL.md` — це той самий формат, який використовує **OpenClaw** (`~/.openclaw` шукає папки з SKILL.md). Коли дійдеш до автоматизації через OpenClaw, ці skills підключаються напряму, без переписування.
- Git-friendly: diff, історія змін, відкат.

## Структура

`skills/` і `docs/` — спільні для всіх історій (story-agnostic пайплайн). Дані конкретної адаптації (реєстри, епізоди, референс-зображення) живуть в окремому фолдері під `stories/<story-slug>/`, щоб різні історії ніколи не змішувались.

```
memoria/
├── README.md                    ← цей файл
├── docs/
│   ├── architecture.md          ← опис пайплайну, принципів і структури для кількох історій
│   ├── business-analysis.md     ← ринок, копірайт, технології, бізнес-модель
│   ├── pilot-plan.md            ← покроковий план пілотного запуску + план автоматизації OpenClaw
│   └── superpowers/
│       ├── specs/                ← архітектурні дизайн-спеки
│       └── plans/                ← implementation-плани
├── skills/                      ← кожен агент пайплайну як SKILL.md (сумісно з OpenClaw, спільний для всіх історій)
│   ├── source-ingestion/
│   ├── master-narrative/
│   ├── scene-intelligence-engine/
│   ├── storyboard-planner/
│   ├── registry-builder/
│   ├── visual-shot-package/
│   ├── prompt-compiler/
│   ├── image-director/
│   ├── narrator-audio-director/
│   └── produce-episode/         ← оркеструє весь пайплайн однією командою (приймає story_slug)
└── stories/                     ← одна папка на кожну адаптовану історію
    └── the-greatest-heretic/    ← story-slug першої історії в роботі
        ├── source-material/
        │   └── master-extract.json   ← накопичені факти з джерела (Source Ingestion)
        ├── registries/                ← Single Source of Truth ЛИШЕ цієї історії
        │   ├── character-registry.json
        │   ├── location-registry.json
        │   ├── prop-registry.json
        │   ├── camera-registry.json
        │   ├── palette-registry.json
        │   └── style-registry.json
        ├── characters/                ← фактичні файли референс-аркушів персонажів
        │   └── CHAR_001/reference.png
        └── episodes/                  ← робочі файли по кожному епізоду цієї історії
            └── ep01/
                ├── script.md              ← редакційний бриф: URL джерела + свідомі зміни
                ├── 00-source-extract.json
                ├── 01-master-narrative.json
                ├── 02-scene-intelligence.json
                ├── 03-storyboard.json
                ├── 04-visual-shot-package.json
                ├── 05-prompt-package.json
                ├── 06-generation-log.json
                ├── generated/             ← фактичні файли згенерованих кадрів (не URL)
                ├── audio/
                └── final/
```

**Нова історія:** створити `stories/<новий-slug>/` за цим самим шаблоном — `skills/` і `docs/` міняти не потрібно.

## Як передати іншій LLM або OpenClaw

**Іншій LLM:** дай їй прочитати `docs/architecture.md` + відповідний `registries/*.json` + `skills/<потрібний>/SKILL.md`. Цього достатньо для повного контексту без історії чату.

**OpenClaw:** вкажи `~/.openclaw/skills` (або відповідний shared-skills шлях) на папку `skills/` з цього репозиторію — кожна підпапка з SKILL.md стає доступною агенту як окремий інструмент.

## Статус проєкту

Пілотна фаза. Дивись `docs/pilot-plan.md` для поточних кроків і чеклиста.
