# Skill: Master Narrative

## Purpose
Перетворює вхідний сценарій/ідею історії у структурований наратив. Джерело істини для всіх наступних етапів пайплайну.

## Input
- Сирий сценарій, синопсис, або опис серії (текст)

## Output
Структуровані наративні сцени (JSON або markdown-список), кожна з:
- scene_id
- summary (коротко, що відбувається)
- characters_present (посилання на character_id з registries/character-registry.json)
- location (посилання на location_id)
- emotional_beat (що відчуває глядач/персонаж)

## Rules
- Ніколи не визначає візуал (це відповідальність Storyboard Planner/Visual Shot Package).
- Не вигадує фактів, яких немає у вхідному сценарії.
- Кожна сцена — окрема одиниця, придатна для подальшої обробки Scene Intelligence Engine.

## Example invocation (концептуально)
"Ось сценарій епізоду 1: [текст]. Побудуй Master Narrative у форматі JSON зі сценами."
