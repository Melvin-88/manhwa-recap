# Skill: Visual Shot Package

## Purpose
Об'єднує storyboard-шот з даними реєстру в повну візуальну специфікацію, готову для компіляції промпту.

## Input
- Шот зі Storyboard Planner
- Відповідні записи з registries/character-registry.json, location-registry.json, prop-registry.json, camera-registry.json, palette-registry.json

## Output
Visual Shot Package (JSON) з повними полями:
- camera (з camera-registry)
- lighting
- composition
- continuity (що має збігатись з попередніми шотами цього персонажа/локації)
- render_constraints
- memory_images (референсні зображення для консистентності)
- emotional_arc (перенесено зі Scene Intelligence)

## Rules
- НЕ генерує текстовий промпт — це відповідальність Prompt Compiler.
- Обов'язково посилається на конкретні reference_image_path з character-registry для кожного персонажа в кадрі.
