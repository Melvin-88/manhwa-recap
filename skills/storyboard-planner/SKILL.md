# Skill: Storyboard Planner

## Purpose
Розбиває сцену (вже збагачену Scene Intelligence Engine) на конкретні кінематографічні шоти.

## Input
Збагачена сцена (з полями scene_intent, emotional_arc тощо)

## Output
Список шотів, кожен з:
- shot_id
- camera_id (посилання на registries/camera-registry.json)
- composition_goal (що глядач має побачити/відчути в цьому кадрі)
- pacing_note (швидкий/повільний, тривалість)
- characters_in_frame

## Rules
- Кожен шот має чітку композиційну ціль, не просто "показати сцену".
- Використовує тільки camera_id з реєстру камер, не вигадує нові пресети на льоту (при потребі — додати в реєстр окремо).
