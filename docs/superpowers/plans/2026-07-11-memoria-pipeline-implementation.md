# Memoria Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реалізувати архітектуру пайплайну з `docs/superpowers/specs/2026-07-11-pipeline-architecture-design.md`: додати нові skill-агенти (Source Ingestion, Narrator/Audio Director, Produce Episode), оновити існуючі `SKILL.md` з конкретними output-схемами, оновити реєстри, перескласти шаблон `episodes/ep01/` за новою нумерацією файлів, синхронізувати `docs/architecture.md` і `README.md`.

**Architecture:** Це репозиторій специфікацій (Markdown/JSON), не виконуваний код — тут немає юніт-тестів у традиційному сенсі. "Тест" кожного кроку — це (а) валідність JSON через `python3 -m json.tool`, (б) наявність обов'язкових секцій/полів через `grep`. Кожен файл редагується повністю (файли короткі, 15-40 рядків), тому кроки дають повний новий вміст файлу, а не diff-патчі.

**Tech Stack:** Markdown, JSON, `python3` (лише для валідації JSON, вже є в системі), `grep`.

## Global Constraints

- Оригінальний текст джерела (веб-новела/манхва) ніколи не зберігається дослівно в жодному файлі репозиторію — тільки факти власними словами (з дизайн-спеку, розділ "Source Ingestion").
- Кожен реєстр (`registries/*.json`) — окремий файл, типи сутностей не змішуються.
- `locked:true` записи в реєстрах ніколи не змінюються без явного підтвердження людини — це правило вже існує в `skills/registry-builder/SKILL.md` і має зберегтись у всіх редакціях.
- Нумерація файлів епізоду фіксована: `00-source-extract.json` → `01-master-narrative.json` → `02-scene-intelligence.json` / `02b-narration-script.json` → `03-storyboard.json` → `04-visual-shot-package.json` → `05-prompt-package.json` → `06-generation-log.json` → `final/<episode_id>.mp4`.
- Генератор для пілоту — `generation_backend: "claude-mcp-media"` (вбудовані MCP-інструменти), `fallback_model` лишається задокументованою неактивною альтернативою.

---

## Task 1: Оновити реєстри (character-registry, style-registry)

**Files:**
- Modify: `registries/character-registry.json` (весь файл)
- Modify: `registries/style-registry.json` (весь файл)

**Interfaces:**
- Produces: поле `voice_id` (замінює `voice_id_elevenlabs`) та `source_name` в `character-registry.json`; поле `generation_backend` (замінює `generator_config.primary_model`) в `style-registry.json`. Усі наступні задачі, що згадують ці поля, посилаються саме на ці назви.

- [ ] **Step 1: Переписати `registries/character-registry.json`**

```json
{
  "_schema_note": "Single Source of Truth для персонажів. Registry Builder читає/пише сюди. Prompt Compiler резолвить character_id в опис при побудові промпту. source_name трасує адаптацію з джерела (Source Ingestion) і ніколи не виводиться в публічний контент.",
  "characters": [
    {
      "character_id": "CHAR_001",
      "name": "",
      "source_name": "",
      "role": "protagonist | antagonist | supporting",
      "appearance": {
        "age_range": "",
        "build": "",
        "hair": "",
        "eyes": "",
        "distinguishing_features": "",
        "default_outfit": ""
      },
      "personality_visual_cues": "",
      "voice_id": "",
      "reference_sheet_path": "characters/CHAR_001/",
      "generator_notes": {
        "preferred_model": "claude-mcp-media",
        "reference_image_count": 5,
        "consistency_notes": ""
      },
      "locked": false
    }
  ]
}
```

- [ ] **Step 2: Переписати `registries/style-registry.json`**

```json
{
  "_schema_note": "Глобальний Style Preset проєкту. Один набір на серіал для візуальної консистентності між епізодами.",
  "project_style": {
    "art_style": "",
    "line_weight": "",
    "shading_approach": "",
    "reference_images": [],
    "generator_config": {
      "generation_backend": "claude-mcp-media",
      "fallback_model": "nano-banana-2",
      "fallback_notes": "Задокументовано, але неактивно. Перехід на пряме API не вимагає змін у Prompt Compiler/Image Director, лише перемикання generation_backend."
    }
  }
}
```

- [ ] **Step 3: Валідація JSON**

Run: `python3 -m json.tool registries/character-registry.json > /dev/null && python3 -m json.tool registries/style-registry.json > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 4: Перевірити, що старі назви полів зникли**

Run: `grep -r "voice_id_elevenlabs\|primary_model.*nano-banana" registries/ || echo CLEAN`
Expected: `CLEAN`

- [ ] **Step 5: Commit**

```bash
git add registries/character-registry.json registries/style-registry.json
git commit -m "feat: update registry schemas for MCP generator and source adaptation tracking"
```

---

## Task 2: Новий skill — Source Ingestion

**Files:**
- Create: `skills/source-ingestion/SKILL.md`

**Interfaces:**
- Consumes: URL(и) джерела + `script.md` епізоду (редакційний бриф)
- Produces: `00-source-extract.json` зі структурою `{episode_id, source_refs[], characters_extracted[], world_facts[], plot_beats[], adaptation_notes{renamed[], compressed[], changed[]}}` — Task 3/4/5a читають саме ці назви полів.

- [ ] **Step 1: Створити `skills/source-ingestion/SKILL.md`**

```markdown
# Skill: Source Ingestion

## Purpose
Перший етап пайплайну. Перетворює готовий розділ(и) джерела (веб-новела/манхва за URL) у структуровані факти — персонажів, світ, сюжетні події — без збереження оригінального тексту дослівно. Це і є момент, де починається трансформація/стиснення історії.

## Input
- Одна або кілька URL-адрес розділів джерела, що покривають один епізод (за раз — один діапазон розділів, ніколи вся новела масово)
- `script.md` епізоду з редакційним брифом (які свідомі зміни вносити)

## Output
`00-source-extract.json`:
```json
{
  "episode_id": "ep01",
  "source_refs": [
    {"url": "https://example.com/chapter-1", "chapters_covered": "1"}
  ],
  "characters_extracted": [
    {
      "source_name": "",
      "adapted_name": "",
      "role": "protagonist | antagonist | supporting",
      "key_traits": []
    }
  ],
  "world_facts": [],
  "plot_beats": [
    {"beat_id": "BEAT_001", "summary": "", "characters_involved": []}
  ],
  "adaptation_notes": {
    "renamed": [],
    "compressed": [],
    "changed": []
  }
}
```

## Rules
- **Оригінальний текст джерела ніколи не зберігається дослівно в жодному файлі репозиторію.** Вихід — факти й короткі власні формулювання, не перефразовані речення оригіналу.
- Вихід має бути суттєво коротшим за джерело.
- Обробляти по одному діапазону розділів за раз — не масовий скрейпінг усієї новели одним викликом.
- Потребує можливості читання веб-сторінки (web fetch / browser tool залежно від агента, що виконує цей skill).
- `adaptation_notes` обов'язкові й конкретні — це основа чекпоінта 0 (людина підтверджує достатність трансформації перед тим, як факти йдуть у Master Narrative).
- Персонажі/локації з `characters_extracted` передаються в Registry Builder для створення unlocked-записів із `source_name` та `adapted_name`.
```

- [ ] **Step 2: Перевірити наявність обов'язкових секцій**

Run: `grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" skills/source-ingestion/SKILL.md`
Expected: `4`

- [ ] **Step 3: Витягти і валідувати JSON-приклад зі схемою**

Run: `sed -n '/```json/,/```/p' skills/source-ingestion/SKILL.md | sed '1d;$d' | python3 -m json.tool > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 4: Commit**

```bash
git add skills/source-ingestion/SKILL.md
git commit -m "feat: add Source Ingestion skill"
```

---

## Task 3: Новий skill — Narrator / Audio Director

**Files:**
- Create: `skills/narrator-audio-director/SKILL.md`

**Interfaces:**
- Consumes: сцени з `01-master-narrative.json` (поля `scene_id`, `summary`, `emotional_beat`) + `voice_id` з `registries/character-registry.json` (з Task 1)
- Produces: `audio/02b-narration-script.json` і `audio/generation-log.json`

- [ ] **Step 1: Створити `skills/narrator-audio-director/SKILL.md`**

```markdown
# Skill: Narrator / Audio Director

## Purpose
Паралельна аудіо-гілка пайплайну. Перетворює сцени з Master Narrative у наративний/діалоговий текст і генерує озвучення, використовуючи закріплені voice_id персонажів. Не залежить від Storyboard/Visual Shot Package — стартує одразу після Master Narrative.

## Input
- Сцени з `01-master-narrative.json` (`scene_id`, `summary`, `emotional_beat`)
- `voice_id` кожного присутнього персонажа з `registries/character-registry.json`

## Output
`audio/02b-narration-script.json`:
```json
{
  "episode_id": "ep01",
  "narration_lines": [
    {
      "scene_id": "",
      "character_id": "",
      "voice_id": "",
      "text": "",
      "emotional_tone": ""
    }
  ]
}
```

`audio/generation-log.json`:
```json
{
  "episode_id": "ep01",
  "generated_assets": [
    {"scene_id": "", "character_id": "", "audio_path": "", "generated_at": "", "flagged_for_review": false}
  ]
}
```

## Rules
- `voice_id` створюється один раз на персонажа (кешується в `character-registry.json`), не перегенеровується щоразу.
- Якщо емоційний тон сцени суттєво розходиться з попереднім використанням голосу цього персонажа — позначає `flagged_for_review: true`, не генерує мовчки (за аналогією з правилом Image Director).
- Не визначає візуал і не залежить від шотів — паралельна гілка, не послідовний крок після Storyboard Planner.
```

- [ ] **Step 2: Перевірити наявність обов'язкових секцій**

Run: `grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" skills/narrator-audio-director/SKILL.md`
Expected: `4`

- [ ] **Step 3: Валідувати обидва JSON-приклади**

Run:
```bash
python3 -c "
import re, json
content = open('skills/narrator-audio-director/SKILL.md').read()
blocks = re.findall(r'\`\`\`json\n(.*?)\`\`\`', content, re.DOTALL)
assert len(blocks) == 2, f'expected 2 json blocks, found {len(blocks)}'
for b in blocks:
    json.loads(b)
print('VALID')
"
```
Expected: `VALID`

- [ ] **Step 4: Commit**

```bash
git add skills/narrator-audio-director/SKILL.md
git commit -m "feat: add Narrator/Audio Director skill"
```

---

## Task 4: Оновити Registry Builder

**Files:**
- Modify: `skills/registry-builder/SKILL.md` (весь файл)

**Interfaces:**
- Consumes: `source_name`/`adapted_name` від Source Ingestion (Task 2), поля `character-registry.json` з Task 1
- Produces: без змін до зовнішнього контракту — уточнює тригер виклику (on-demand, вперше після Source Ingestion)

- [ ] **Step 1: Переписати `skills/registry-builder/SKILL.md`**

```markdown
# Skill: Registry Builder

## Purpose
Підтримує та оновлює незмінні (у межах епізоду) реєстри: Character, Location, Prop, Camera, Palette, Style. Єдине джерело істини для всіх візуальних сутностей проєкту.

## Input
Запит на створення/оновлення запису в одному з реєстрів `registries/*.json`. Викликається на вимогу (не послідовний етап): вперше одразу після Source Ingestion (нові персонажі з `source_name`/`adapted_name`), повторно під час Storyboard Planner, якщо з'являються нові локації/пропси.

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
  "reference_sheet_path": "characters/CHAR_002/",
  "generator_notes": { "preferred_model": "claude-mcp-media", "reference_image_count": 5, "consistency_notes": "" },
  "locked": false
}
```

## Rules
- Ніколи не змінює існуючий `locked:true` запис без явного підтвердження людини.
- Нові персонажі/локації отримують character sheet / reference image перед тим, як `locked:true`.
- Кожен реєстр — окремий файл, не змішувати типи сутностей в одному файлі.
- Записи персонажів, створені з Source Ingestion, обов'язково заповнюють `source_name` для трасування адаптації (ніколи не виводиться в публічний контент).
```

- [ ] **Step 2: Перевірити, що правило про `locked:true` збереглось**

Run: `grep -q "locked:true" skills/registry-builder/SKILL.md && echo OK`
Expected: `OK`

- [ ] **Step 3: Валідувати JSON-приклад**

Run: `sed -n '/```json/,/```/p' skills/registry-builder/SKILL.md | sed '1d;$d' | python3 -m json.tool > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 4: Commit**

```bash
git add skills/registry-builder/SKILL.md
git commit -m "docs: clarify Registry Builder on-demand trigger from Source Ingestion"
```

---

## Task 5a: Оновити Master Narrative, Scene Intelligence Engine, Storyboard Planner

**Files:**
- Modify: `skills/master-narrative/SKILL.md` (весь файл)
- Modify: `skills/scene-intelligence-engine/SKILL.md` (весь файл)
- Modify: `skills/storyboard-planner/SKILL.md` (весь файл)

**Interfaces:**
- Consumes: `00-source-extract.json` (Task 2)
- Produces: `01-master-narrative.json`, `02-scene-intelligence.json`, `03-storyboard.json` — Task 5b і Task 6 посилаються на ці назви файлів і поля `scene_id`, `shot_id`, `camera_id`.

- [ ] **Step 1: Переписати `skills/master-narrative/SKILL.md`**

```markdown
# Skill: Master Narrative

## Purpose
Перетворює структуровані факти від Source Ingestion у структурований наратив власною прозою. Джерело істини для всіх наступних етапів пайплайну. Момент трансформації/стиснення історії — не Source Ingestion.

## Input
`00-source-extract.json` від Source Ingestion (факти: персонажі, world_facts, plot_beats, adaptation_notes) + `script.md` (редакційний бриф людини: обсяг епізоду, свідомі зміни)

## Output
`01-master-narrative.json`:
```json
{
  "episode_id": "ep01",
  "scenes": [
    {
      "scene_id": "SCENE_001",
      "summary": "",
      "characters_present": [],
      "location": "",
      "emotional_beat": ""
    }
  ]
}
```

## Rules
- Ніколи не визначає візуал (це відповідальність Storyboard Planner/Visual Shot Package).
- Пише власну прозу на основі фактів з `00-source-extract.json` — не перефразовує оригінальний текст джерела, бо його в файлі й немає (лише факти).
- Кожна сцена — окрема одиниця, придатна для подальшої обробки Scene Intelligence Engine.

## Example invocation (концептуально)
"Ось факти з 00-source-extract.json для епізоду 1: [JSON]. Побудуй Master Narrative у форматі 01-master-narrative.json зі сценами."
```

- [ ] **Step 2: Переписати `skills/scene-intelligence-engine/SKILL.md`**

```markdown
# Skill: Scene Intelligence Engine

## Purpose
Аналізує кожну сцену з Master Narrative і витягує глибші структурні дані, потрібні для storyboard.

## Input
Одна сцена з `01-master-narrative.json`

## Output
`02-scene-intelligence.json`:
```json
{
  "episode_id": "ep01",
  "scenes": [
    {
      "scene_id": "SCENE_001",
      "scene_intent": "",
      "emotional_arc": "",
      "chronology_position": "",
      "continuity_requirements": [],
      "entities": [],
      "environment_logic": ""
    }
  ]
}
```

## Rules
- Спирається лише на дані з Master Narrative та реєстрів, нічого не вигадує.
- Не визначає композицію кадру (це Storyboard Planner).
```

- [ ] **Step 3: Переписати `skills/storyboard-planner/SKILL.md`**

```markdown
# Skill: Storyboard Planner

## Purpose
Розбиває сцену (вже збагачену Scene Intelligence Engine) на конкретні кінематографічні шоти.

## Input
Збагачена сцена з `02-scene-intelligence.json`

## Output
`03-storyboard.json`:
```json
{
  "episode_id": "ep01",
  "shots": [
    {
      "shot_id": "SHOT_001",
      "scene_id": "SCENE_001",
      "camera_id": "",
      "composition_goal": "",
      "pacing_note": "",
      "characters_in_frame": []
    }
  ]
}
```

## Rules
- Кожен шот має чітку композиційну ціль, не просто "показати сцену".
- Використовує тільки `camera_id` з `registries/camera-registry.json`, не вигадує нові пресети на льоту (при потребі — викликає Registry Builder).
```

- [ ] **Step 4: Перевірити наявність обов'язкових секцій у всіх трьох файлах**

Run: `for f in skills/master-narrative/SKILL.md skills/scene-intelligence-engine/SKILL.md skills/storyboard-planner/SKILL.md; do c=$(grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" "$f"); echo "$f: $c"; done`
Expected: усі три рядки показують `4` (окрім master-narrative, де є ще `## Example invocation` — рахуємо лише 4 обов'язкові секції, тому теж `4`)

- [ ] **Step 5: Валідувати всі три JSON-приклади**

Run: `for f in skills/master-narrative/SKILL.md skills/scene-intelligence-engine/SKILL.md skills/storyboard-planner/SKILL.md; do sed -n '/```json/,/```/p' "$f" | sed '1d;$d' | python3 -m json.tool > /dev/null && echo "$f VALID"; done`
Expected:
```
skills/master-narrative/SKILL.md VALID
skills/scene-intelligence-engine/SKILL.md VALID
skills/storyboard-planner/SKILL.md VALID
```

- [ ] **Step 6: Commit**

```bash
git add skills/master-narrative/SKILL.md skills/scene-intelligence-engine/SKILL.md skills/storyboard-planner/SKILL.md
git commit -m "docs: add concrete output schemas to narrative/scene/storyboard skills"
```

---

## Task 5b: Оновити Visual Shot Package, Prompt Compiler, Image Director

**Files:**
- Modify: `skills/visual-shot-package/SKILL.md` (весь файл)
- Modify: `skills/prompt-compiler/SKILL.md` (весь файл)
- Modify: `skills/image-director/SKILL.md` (весь файл)

**Interfaces:**
- Consumes: `03-storyboard.json` (Task 5a), `generation_backend` зі `style-registry.json` (Task 1)
- Produces: `04-visual-shot-package.json`, `05-prompt-package.json`, `06-generation-log.json` — Task 6 і Task 7 посилаються на ці назви.

- [ ] **Step 1: Переписати `skills/visual-shot-package/SKILL.md`**

```markdown
# Skill: Visual Shot Package

## Purpose
Об'єднує storyboard-шот з даними реєстру в повну візуальну специфікацію, готову для компіляції промпту.

## Input
- Шот з `03-storyboard.json`
- Відповідні записи з `registries/character-registry.json`, `location-registry.json`, `prop-registry.json`, `camera-registry.json`, `palette-registry.json`

## Output
`04-visual-shot-package.json`:
```json
{
  "episode_id": "ep01",
  "shot_packages": [
    {
      "shot_id": "SHOT_001",
      "camera": {},
      "lighting": "",
      "composition": "",
      "continuity": "",
      "render_constraints": "",
      "memory_images": [],
      "emotional_arc": ""
    }
  ]
}
```

## Rules
- НЕ генерує текстовий промпт — це відповідальність Prompt Compiler.
- Обов'язково посилається на конкретні `reference_image_path` з character-registry для кожного персонажа в кадрі.
```

- [ ] **Step 2: Переписати `skills/prompt-compiler/SKILL.md`**

```markdown
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
```

- [ ] **Step 3: Переписати `skills/image-director/SKILL.md`**

```markdown
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
```

- [ ] **Step 4: Перевірити наявність обов'язкових секцій у всіх трьох файлах**

Run: `for f in skills/visual-shot-package/SKILL.md skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md; do c=$(grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" "$f"); echo "$f: $c"; done`
Expected: усі три рядки показують `4`

- [ ] **Step 5: Валідувати всі три JSON-приклади**

Run: `for f in skills/visual-shot-package/SKILL.md skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md; do sed -n '/```json/,/```/p' "$f" | sed '1d;$d' | python3 -m json.tool > /dev/null && echo "$f VALID"; done`
Expected:
```
skills/visual-shot-package/SKILL.md VALID
skills/prompt-compiler/SKILL.md VALID
skills/image-director/SKILL.md VALID
```

- [ ] **Step 6: Перевірити, що generation_backend згадано в prompt-compiler і image-director**

Run: `grep -l "generation_backend" skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md | wc -l`
Expected: `2`

- [ ] **Step 7: Commit**

```bash
git add skills/visual-shot-package/SKILL.md skills/prompt-compiler/SKILL.md skills/image-director/SKILL.md
git commit -m "docs: add concrete output schemas and MCP generator binding to compilation skills"
```

---

## Task 6: Новий skill — Produce Episode (оркестратор)

**Files:**
- Create: `skills/produce-episode/SKILL.md`

**Interfaces:**
- Consumes: усі назви файлів і полів з Task 1–5b (`00-source-extract.json` … `06-generation-log.json`, `audio/*.json`, `locked`, `flagged_for_review`)
- Produces: немає нового формату даних — лише послідовність викликів і чекпоінтів, яку читає людина (і пізніше OpenClaw)

- [ ] **Step 1: Створити `skills/produce-episode/SKILL.md`**

```markdown
# Skill: Produce Episode

## Purpose
Оркеструє повний пайплайн виробництва одного епізоду: викликає всі skill-агенти по порядку, читає/пише файли епізоду за фіксованою нумерацією, зупиняється на чекпоінтах людського підтвердження. Це єдина команда, якою людина запускає весь процес — не 8 окремих команд.

## Input
- `episode_id` (наприклад `ep02`)
- `episodes/<episode_id>/script.md` — редакційний бриф: URL(и) джерела, обсяг епізоду, свідомі зміни

## Sequence

1. **Source Ingestion** → пише `episodes/<episode_id>/00-source-extract.json`
   → **ЧЕКПОІНТ 0**: показати `adaptation_notes` людині, чекати підтвердження достатньої трансформації
2. **Registry Builder** (on-demand) → створює unlocked-записи нових персонажів/локацій у `registries/*.json`
   → **ЧЕКПОІНТ 2**: показати нові записи, чекати `locked:true` від людини
3. **Master Narrative** → пише `episodes/<episode_id>/01-master-narrative.json`
   → **ЧЕКПОІНТ 1**: показати розбивку на сцени, чекати підтвердження
4. Паралельно (незалежні гілки, можна виконувати в будь-якому порядку):
   - **Візуальна гілка**: Scene Intelligence Engine → `02-scene-intelligence.json` → Storyboard Planner → `03-storyboard.json` (виклик Registry Builder on-demand, якщо з'являються нові локації/пропси) → Visual Shot Package → `04-visual-shot-package.json` → Prompt Compiler → `05-prompt-package.json`
     → **ЧЕКПОІНТ 3**: показати список шотів і скомпільовані промпти, чекати підтвердження перед витратою викликів генерації
     → Image Director → `06-generation-log.json` (позначає `flagged_for_review` замість мовчазної генерації)
   - **Аудіо гілка**: Narrator/Audio Director → `audio/02b-narration-script.json` → `audio/generation-log.json` (позначає `flagged_for_review` замість мовчазної генерації)
5. **Assembly** (механічний скрипт, не LLM-виклик) → збирає `06-generation-log.json` + `audio/generation-log.json` у `episodes/<episode_id>/final/<episode_id>.mp4`
   → **ЧЕКПОІНТ 5**: показати відео, чекати рішення про публікацію

## Rules
- Кожен крок читає лише файл(и), явно перелічені в `Input` відповідного skill — ніколи не "згадує" дані з попередньої розмови в обхід файлу.
- Зупинка на чекпоінті означає: показати людині конкретний артефакт (JSON/список/відео) і дослівно чекати на підтвердження в чаті, перш ніж читати наступний skill.
- Якщо людина після чекпоінта редагує проміжний файл вручну (наприклад, править `01-master-narrative.json`) — наступний крок пайплайну читає відредаговану версію, не оригінальний вивід агента.
- Будь-який крок можна перезапустити ізольовано (наприклад, "перегенеруй тільки 03-storyboard.json") — це просто повторний виклик відповідного skill з тим самим файлом на вході.
```

- [ ] **Step 2: Перевірити, що всі 5 чекпоінтів згадані**

Run: `grep -c "ЧЕКПОІНТ" skills/produce-episode/SKILL.md`
Expected: `5`

- [ ] **Step 3: Перевірити, що всі назви файлів пайплайну присутні**

Run: `for name in 00-source-extract.json 01-master-narrative.json 02-scene-intelligence.json 02b-narration-script.json 03-storyboard.json 04-visual-shot-package.json 05-prompt-package.json 06-generation-log.json; do grep -q "$name" skills/produce-episode/SKILL.md || echo "MISSING: $name"; done; echo DONE`
Expected: `DONE` (без жодного `MISSING`)

- [ ] **Step 4: Commit**

```bash
git add skills/produce-episode/SKILL.md
git commit -m "feat: add Produce Episode orchestrating skill"
```

---

## Task 7: Перескласти шаблон episodes/ep01 за новою нумерацією

**Files:**
- Modify: `episodes/ep01/script.md` (весь файл)
- Create: `episodes/ep01/00-source-extract.json`
- Create: `episodes/ep01/01-master-narrative.json`
- Create: `episodes/ep01/02-scene-intelligence.json`
- Create: `episodes/ep01/03-storyboard.json`
- Create: `episodes/ep01/04-visual-shot-package.json`
- Create: `episodes/ep01/05-prompt-package.json`
- Create: `episodes/ep01/06-generation-log.json`
- Create: `episodes/ep01/audio/02b-narration-script.json`
- Create: `episodes/ep01/audio/generation-log.json`
- Create: `episodes/ep01/final/.gitkeep`
- Delete: `episodes/ep01/shot-package.json` (замінено на `04-visual-shot-package.json`)
- Delete: `episodes/ep01/prompts.json` (замінено на `05-prompt-package.json`)

**Interfaces:**
- Consumes: усі схеми з Task 2–5b
- Produces: робочий шаблон епізоду, який Task 8 описує в документації

- [ ] **Step 1: Переписати `episodes/ep01/script.md`**

```markdown
# Episode 01 — [Робоча назва]

## Джерело
- URL(и) розділів: [посилання на джерело]
- Розділи, що покриває цей епізод: [напр. 1-3]

## Свідомі зміни (для Source Ingestion / Master Narrative)
- [напр. "скоротити арку X до однієї сцени"]
- [напр. "змінити ім'я персонажа Y"]

## Нотатки
- Персонажі, що з'являються вперше: ...
- Нові локації: ...
```

- [ ] **Step 2: Створити нові порожні артефакти пайплайну**

`episodes/ep01/00-source-extract.json`:
```json
{
  "episode_id": "ep01",
  "source_refs": [],
  "characters_extracted": [],
  "world_facts": [],
  "plot_beats": [],
  "adaptation_notes": { "renamed": [], "compressed": [], "changed": [] }
}
```

`episodes/ep01/01-master-narrative.json`:
```json
{
  "episode_id": "ep01",
  "scenes": []
}
```

`episodes/ep01/02-scene-intelligence.json`:
```json
{
  "episode_id": "ep01",
  "scenes": []
}
```

`episodes/ep01/03-storyboard.json`:
```json
{
  "episode_id": "ep01",
  "shots": []
}
```

`episodes/ep01/04-visual-shot-package.json`:
```json
{
  "episode_id": "ep01",
  "shot_packages": []
}
```

`episodes/ep01/05-prompt-package.json`:
```json
{
  "episode_id": "ep01",
  "prompt_packages": []
}
```

`episodes/ep01/06-generation-log.json`:
```json
{
  "episode_id": "ep01",
  "generated_assets": []
}
```

`episodes/ep01/audio/02b-narration-script.json`:
```json
{
  "episode_id": "ep01",
  "narration_lines": []
}
```

`episodes/ep01/audio/generation-log.json`:
```json
{
  "episode_id": "ep01",
  "generated_assets": []
}
```

- [ ] **Step 3: Створити плейсхолдер для порожньої директорії final/**

Run: `touch episodes/ep01/final/.gitkeep`

- [ ] **Step 4: Видалити застарілі файли**

Run: `git rm episodes/ep01/shot-package.json episodes/ep01/prompts.json`

- [ ] **Step 5: Валідувати всі нові JSON-файли**

Run: `for f in episodes/ep01/00-source-extract.json episodes/ep01/01-master-narrative.json episodes/ep01/02-scene-intelligence.json episodes/ep01/03-storyboard.json episodes/ep01/04-visual-shot-package.json episodes/ep01/05-prompt-package.json episodes/ep01/06-generation-log.json episodes/ep01/audio/02b-narration-script.json episodes/ep01/audio/generation-log.json; do python3 -m json.tool "$f" > /dev/null && echo "$f VALID"; done`
Expected: усі 9 файлів виводять `VALID`

- [ ] **Step 6: Перевірити, що застарілі файли справді зникли**

Run: `test -f episodes/ep01/shot-package.json && echo STILL_EXISTS || echo REMOVED; test -f episodes/ep01/prompts.json && echo STILL_EXISTS || echo REMOVED`
Expected:
```
REMOVED
REMOVED
```

- [ ] **Step 7: Commit**

```bash
git add episodes/ep01/
git commit -m "feat: restructure ep01 template to numbered pipeline artifact convention"
```

---

## Task 8: Синхронізувати docs/architecture.md і README.md

**Files:**
- Modify: `docs/architecture.md` (секції Pipeline, стадії, Registry System, Current JSON Artifacts, Open Items)
- Modify: `README.md` (секція Структура)

**Interfaces:**
- Consumes: фінальний список skills/файлів з Task 1–7
- Produces: немає — це документація, кінцевий артефакт для читання людиною/іншою LLM

- [ ] **Step 1: Замінити секцію `## Pipeline` в `docs/architecture.md`**

Знайти блок від `## Pipeline` до кінця опису `Image Director` (перед `## Registry System`) і замінити на:

```markdown
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
Підтримує незмінні реєстри: Character, Location, Prop, Camera, Palette, Style, Generator. Діє як Single Source of Truth. Викликається на вимогу — вперше одразу після Source Ingestion, повторно під час Storyboard Planner.

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
```

- [ ] **Step 2: Оновити секцію `## Current JSON Artifacts` в `docs/architecture.md`**

Замінити рядок `Resolved Shot Package → Visual Shot Package → Prompt Package.` на:

```markdown
`00-source-extract.json` → `01-master-narrative.json` → `02-scene-intelligence.json` (+ паралельно `audio/02b-narration-script.json`) → `03-storyboard.json` → `04-visual-shot-package.json` → `05-prompt-package.json` → `06-generation-log.json` (+ `audio/generation-log.json`) → `final/<episode_id>.mp4`. Повний контракт полів кожного файлу — у відповідному `skills/<name>/SKILL.md`, секція Output.
```

- [ ] **Step 3: Оновити секцію `## Open Items` в `docs/architecture.md`**

Замінити на:

```markdown
## Open Items (перенести в реєстри при заповненні)

- [ ] Наповнити `registries/character-registry.json` для поточної історії (адаптованої з джерела)
- [ ] Наповнити `registries/style-registry.json` (референс-зображення, палітра, лінія)
- [ ] Обрати конкретне джерело (URL веб-новели/манхви) для першого епізоду
```

- [ ] **Step 4: Оновити структуру в `README.md`**

Знайти блок дерева файлів (```` ``` memoria/ ... ```` ) і замінити на:

```markdown
```
memoria/
├── README.md                    ← цей файл
├── docs/
│   ├── architecture.md          ← опис пайплайну і принципів
│   ├── business-analysis.md     ← ринок, копірайт, технології, бізнес-модель
│   ├── pilot-plan.md            ← покроковий план пілотного запуску + план автоматизації OpenClaw
│   └── superpowers/
│       ├── specs/                ← архітектурні дизайн-спеки
│       └── plans/                ← implementation-плани
├── registries/                  ← Single Source of Truth: персонажі, локації, стиль тощо
│   ├── character-registry.json
│   ├── location-registry.json
│   ├── prop-registry.json
│   ├── camera-registry.json
│   ├── palette-registry.json
│   └── style-registry.json
├── characters/                  ← character sheets (референсні зображення + опис) по кожному персонажу
├── skills/                      ← кожен агент пайплайну як SKILL.md (сумісно з OpenClaw)
│   ├── source-ingestion/
│   ├── master-narrative/
│   ├── scene-intelligence-engine/
│   ├── storyboard-planner/
│   ├── registry-builder/
│   ├── visual-shot-package/
│   ├── prompt-compiler/
│   ├── image-director/
│   ├── narrator-audio-director/
│   └── produce-episode/         ← оркеструє весь пайплайн однією командою
└── episodes/                    ← робочі файли по кожному епізоду
    └── ep01/
        ├── script.md              ← редакційний бриф: URL джерела + свідомі зміни
        ├── 00-source-extract.json
        ├── 01-master-narrative.json
        ├── 02-scene-intelligence.json
        ├── 03-storyboard.json
        ├── 04-visual-shot-package.json
        ├── 05-prompt-package.json
        ├── 06-generation-log.json
        ├── audio/
        └── final/
```
```

- [ ] **Step 5: Перевірити, що нові skill-папки згадані в обох файлах**

Run: `for name in source-ingestion narrator-audio-director produce-episode; do grep -l "$name" docs/architecture.md README.md; done`
Expected: кожен з трьох `name` знаходиться хоча б в одному з двох файлів (мінімум 3 рядки виводу сумарно)

- [ ] **Step 6: Commit**

```bash
git add docs/architecture.md README.md
git commit -m "docs: sync architecture.md and README.md with new pipeline stages and file layout"
```

---

## Фінальна перевірка репозиторію

- [ ] **Step 1: Усі JSON-файли репозиторію валідні**

Run: `find registries episodes -name "*.json" -exec python3 -m json.tool {} \; > /dev/null && echo ALL_VALID`
Expected: `ALL_VALID`

- [ ] **Step 2: Усі SKILL.md мають 4 обов'язкові секції**

Run: `for f in skills/*/SKILL.md; do c=$(grep -c "^## Purpose\|^## Input\|^## Output\|^## Rules" "$f"); [ "$c" -lt 4 ] && echo "INCOMPLETE: $f ($c)"; done; echo CHECK_DONE`
Expected: `CHECK_DONE` без жодного `INCOMPLETE`

- [ ] **Step 3: git status чистий (усе закомічено)**

Run: `git status --short`
Expected: порожній вивід
