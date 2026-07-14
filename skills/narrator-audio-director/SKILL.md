# Skill: Narrator / Audio Director

## Purpose
The pipeline's parallel audio branch. Turns Master Narrative scenes into narration/dialogue text and generates voice, using each character's locked voice_id. Independent of Storyboard/Visual Shot Package — starts right after Master Narrative.

## Input
- Scenes from `01-master-narrative.json` (`scene_id`, `summary`, `emotional_beat`)
- Each present character's `voice_ids[language]` from `registries/character-registry.json`
- `languages` from `stories/<story_slug>/story-config.json` — the list of languages to generate text and audio for

## Output
Multi-language: everything below is generated **separately for each language** in `story-config.json.languages`, in its own subdirectory `audio/<lang>/` (e.g. `audio/uk/`, `audio/en/`) — each language's text, audio files, and log are fully independent of one another.

`audio/<lang>/02b-narration-script.json`:
```json
{
  "episode_id": "ep01",
  "language": "uk",
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

`audio/<lang>/generation-log.json`:
```json
{
  "episode_id": "ep01",
  "language": "uk",
  "generated_assets": [
    {"scene_id": "", "character_id": "", "audio_path": "", "generated_at": "", "flagged_for_review": false}
  ]
}
```

## Rules
- `voice_id` in `narration_lines` is taken from that character's `voice_ids[lang]` in `character-registry.json` for the language currently being generated — never carried over from another language, even temporarily. If a character doesn't yet have a `voice_ids` entry for one of the languages in `story-config.json.languages`, that's a blocker — pick and record a voice first (via the same A/B voice-selection process), then generate text/audio in that language.
- **The text in `narration_lines[].text` is translated independently for each language**, rather than re-voicing one canonical text with different voices. The translation preserves the style and granularity described below — it's an equivalent translation-adaptation, not a literal gloss.
- `voice_id` is created once per character per language (cached in `voice_ids[lang]` in `character-registry.json`), never regenerated on every call.
- If a scene's emotional tone diverges significantly from that character's previous voice usage, flags `flagged_for_review: true` rather than generating silently (by analogy with the Image Director rule).
- Doesn't define visuals and doesn't depend on shots — it's a parallel branch, not a sequential step after Storyboard Planner. The visual branch (frames) is shared across all languages and generated only once.

## Style of the Narration Text (`text` in `narration_lines`)
Reference point: the format used by popular manhwa/novel-recap channels (conversational, "this is happening right now," not literary prose meant to be read silently). Specific rules:
- **First-person narration by the episode's protagonist.** The narrator is the episode's protagonist themselves, retelling their own story as lived experience: "I come to," "I get hit," "I decide to play dumb" — never "he comes to," never an impersonal observing narrator. For lines where the protagonist is the subject of the action or present in the scene, `character_id` is the protagonist's own `character_id` (not a separate `"NARRATOR"` value), and `voice_id` comes from that character's `voice_ids[lang]` entry in `character-registry.json` for the language currently being generated.
  - **The "meanwhile" exception:** if a scene in `01-master-narrative.json` doesn't include the protagonist in `characters_present` (they are not physically present and couldn't have known about it at the time), the line is delivered as a brief aside from the same narrator voice — "Meanwhile, as I'd learn later..." — rather than inventing the protagonist's presence somewhere they aren't. This is the same device used in popular recap videos: first-person narration overall, with rare, clearly marked departures to other characters when the plot requires it.
- **Present tense**, not past: "I wake up," "I say," "I shout" — not "I woke up," "I said." Creates a "happening right here, right now" effect rather than a recap of an already-finished story.
- **Direct attribution by name for other characters' lines, first-person direct voice for the protagonist.** Other characters' lines are conveyed in reported speech with clear attribution ("[Character] says that..."), while the protagonist's own lines, decisions, and reactions read as their inner voice ("I decide...", "I'm scared, but..."). Every meaningful beat in a scene is its own unit with a clear attribution of who is speaking or reacting, rather than a generalized authorial summary.
- **Fine granularity**: every key line or micro-reaction (shock, rage, a smile, hesitation) is its own short beat of text, rather than one compressed sentence for the whole scene. A given `narration_line`'s length adapts accordingly — a scene with active dialogue will run longer than a scene with no lines.
- **Short declarative sentences**, joined with simple connectors ("then," "so," "suddenly," "but," "when") — no complex, multi-level subordinate clauses.
- The source of facts for lines is the same as for the rest of the pipeline: only what's already recorded in `master-extract.json`/`01-master-narrative.json` (no new invented quotes unconnected to recorded facts).
