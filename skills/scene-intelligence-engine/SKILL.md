# Skill: Scene Intelligence Engine

## Purpose
Analyzes each scene from Master Narrative and extracts the deeper structural data the storyboard needs.

## Input
One scene from `01-master-narrative.json`

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
- Relies only on data from Master Narrative and the registries — invents nothing.
- Doesn't define shot composition (that's Storyboard Planner's job).
