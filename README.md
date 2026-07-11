# Memoria — AI Content Pipeline

Registry-driven pipeline для генерації озвучених серій з AI-згенерованими зображеннями (формат "аудіокнига з картинками").

## Навіщо ця структура

Все в цьому репозиторії — звичайний Markdown/JSON. Жодних форматів, специфічних для однієї LLM. Це означає:
- Будь-яка LLM (Claude, GPT, Gemini, локальна модель) може прочитати весь контекст проєкту, просто відкривши файли.
- Структура `skills/<name>/SKILL.md` — це той самий формат, який використовує **OpenClaw** (`~/.openclaw` шукає папки з SKILL.md). Коли дійдеш до автоматизації через OpenClaw, ці skills підключаються напряму, без переписування.
- Git-friendly: diff, історія змін, відкат.

## Структура

```
memoria/
├── README.md                    ← цей файл
├── docs/
│   ├── architecture.md          ← опис пайплайну і принципів (з оригінального Word-документа)
│   ├── business-analysis.md     ← ринок, копірайт, технології, бізнес-модель
│   └── pilot-plan.md            ← покроковий план пілотного запуску + план автоматизації OpenClaw
├── registries/                  ← Single Source of Truth: персонажі, локації, стиль тощо
│   ├── character-registry.json
│   ├── location-registry.json
│   ├── prop-registry.json
│   ├── camera-registry.json
│   ├── palette-registry.json
│   └── style-registry.json
├── characters/                  ← character sheets (референсні зображення + опис) по кожному персонажу
├── skills/                      ← кожен агент пайплайну як SKILL.md (сумісно з OpenClaw)
│   ├── master-narrative/
│   ├── scene-intelligence-engine/
│   ├── storyboard-planner/
│   ├── registry-builder/
│   ├── visual-shot-package/
│   ├── prompt-compiler/
│   └── image-director/
└── episodes/                    ← робочі файли по кожному епізоду
    └── ep01/
        ├── script.md            ← сценарій/наратив
        ├── shot-package.json    ← Visual Shot Package
        └── prompts.json         ← скомпільовані промпти для генератора
```

## Як передати іншій LLM або OpenClaw

**Іншій LLM:** дай їй прочитати `docs/architecture.md` + відповідний `registries/*.json` + `skills/<потрібний>/SKILL.md`. Цього достатньо для повного контексту без історії чату.

**OpenClaw:** вкажи `~/.openclaw/skills` (або відповідний shared-skills шлях) на папку `skills/` з цього репозиторію — кожна підпапка з SKILL.md стає доступною агенту як окремий інструмент.

## Статус проєкту

Пілотна фаза. Дивись `docs/pilot-plan.md` для поточних кроків і чеклиста.
