# Skill: Scene Intelligence Engine

## Purpose
Аналізує кожну сцену з Master Narrative і витягує глибші структурні дані, потрібні для storyboard.

## Input
Одна сцена з Master Narrative (JSON)

## Output
Розширена сцена з полями:
- scene_intent (навіщо ця сцена існує в історії)
- emotional_arc (з чого в що змінюється настрій)
- chronology_position (де в часовій лінії)
- continuity_requirements (що має лишатись незмінним з попередніх сцен — одяг, поранення, погода)
- entities (усі персонажі/об'єкти, що фігурують)
- environment_logic (чому середовище виглядає саме так у цей момент)

## Rules
- Спирається лише на дані з Master Narrative та реєстрів, нічого не вигадує.
- Не визначає композицію кадру (це Storyboard Planner).
