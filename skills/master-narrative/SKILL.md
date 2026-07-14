# Skill: Master Narrative

## Purpose
Turns Source Ingestion's structured facts into a structured narrative in its own prose. The source of truth for every later pipeline stage. This is where the story's transformation/compression happens — not Source Ingestion.

## Input
`00-source-extract.json` from Source Ingestion (facts: characters, world_facts, plot_beats, adaptation_notes) + `script.md` (the human's editorial brief: episode scope, deliberate changes)

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
- Never defines visuals (that's Storyboard Planner's/Visual Shot Package's responsibility).
- Writes its own prose based on the facts in `00-source-extract.json` — doesn't paraphrase the original source text, because that text isn't in the file at all (only facts are).
- Each scene is a standalone unit, ready for further processing by Scene Intelligence Engine.

## Example Invocation (conceptual)
"Here are the facts from 00-source-extract.json for episode 1: [JSON]. Build a Master Narrative in the 01-master-narrative.json format with scenes."
