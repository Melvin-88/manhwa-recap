# Skill: Source Ingestion

## Purpose
The pipeline's first stage. Transforms a source (web novel/manhwa) into structured facts — characters, world, plot events — without ever storing the original text verbatim. Operates at the whole-work level: facts accumulate in a single master file incrementally, in batches by volume, rather than being re-derived per episode. This is the point where the story's transformation/compression begins.

## Onboarding a New Story (one-time procedure, BEFORE the first ingestion batch)

When the human provides a link to a new work — before reading any of the source:

1. **The human provides a link to the source** (the work's root URL).
2. **Fix the language(s).** Ask the human which language (or languages) the narration/subtitles for this story's episodes will use, and record the answer in `stories/<story_slug>/story-config.json` (`languages`, `default_language` — schema in Produce Episode's Input). This is a story-level decision made once here, not re-asked per episode.
3. **Collect the work: all data and the original source, by volume, for fast access later.** This is Source Ingestion's core job — see Input/Output/Rules below. The goal is that later episodes and regenerations never need to re-fetch the source live.

Once onboarding is done, move on to Produce Episode (the "process by volume: scripts, prompts, generation" step) for a specific episode, and finally to a human double-check of the finished video (Produce Episode, CHECKPOINT 5).

## Input
- `story_slug` — determines the `stories/<story_slug>/` folder where all of this work's material lives (registries, episodes, character reference images); `work_slug` below is the same value
- The work's root URL, plus a list of already-processed chapters (to know where to resume)
- The existing `stories/<story_slug>/source-material/master-extract.json`, if this isn't the first pass (new facts are appended to existing ones, never overwritten)

## Output
`stories/<story_slug>/source-material/master-extract.json` — an accumulating fact store for the whole work:
```json
{
  "work_slug": "<story-slug>",
  "source_root_url": "https://example.com/work",
  "chapters_ingested": [
    {"chapter": "v1c1", "url": "https://example.com/chapter-1"}
  ],
  "characters_extracted": [
    {
      "source_name": "",
      "adapted_name": "",
      "role": "protagonist | antagonist | supporting",
      "key_traits": [],
      "first_appeared_chapter": "v1c1",
      "auto_generated_fields": []
    }
  ],
  "world_facts": [
    {"fact": "", "first_appeared_chapter": "v1c1"}
  ],
  "plot_beats": [
    {"beat_id": "BEAT_001", "chapter": "v1c1", "summary": "", "characters_involved": []}
  ],
  "adaptation_notes": {
    "renamed": [],
    "compressed": [],
    "changed": []
  }
}
```

The episode-level `00-source-extract.json` is no longer a separate ingestion run — it's a **slice** of `master-extract.json` for the range of `plot_beats`/chapters that fall within a specific episode (path relative to the `stories/<story_slug>/` root):
```json
{
  "episode_id": "ep01",
  "master_extract_ref": "source-material/master-extract.json",
  "beat_range": ["BEAT_001", "BEAT_009"],
  "chapters_covered": ["v1c1", "v1c2"]
}
```

## Detailed Per-Chapter File (standard output of every ingestion pass)

`master-extract.json`'s `plot_beats` is deliberately compressed (1 line = an entire scene) — enough for planning an episode's structure, but not enough detail (appearance, sensory detail, action sequencing, paraphrased dialogue) for writing rich prompts/narration. So for **every** chapter that goes through ingestion, Source Ingestion immediately creates `stories/<story_slug>/source-material/v<N>/c<M>-detailed.json` — without waiting for a separate request from Prompt Compiler:
```json
{
  "chapter": "v1c1",
  "source_url": "",
  "extraction_note": "",
  "detailed_beats": [
    {
      "beat_id": "BEAT_001",
      "maps_to_scene": "SCENE_001",
      "summary": "",
      "visual_details": [],
      "sensory_details": [],
      "internal_monologue_paraphrase": "",
      "dialogue_paraphrase": []
    }
  ]
}
```
- The same "never verbatim" principle applies here just as strictly as to `master-extract.json` — this is an expanded, ORIGINAL retelling (more beats per chapter, each beat described in several points instead of one line), not a closer paraphrase of the source. `dialogue_paraphrase`/`internal_monologue_paraphrase` are always a retelling in the agent's own words, never quotation marks around the original text.
- Created immediately during chapter ingestion, alongside writing the matching `plot_beats` into `master-extract.json` — both outputs of one pass, not two separate steps done at different times.
- Once created, the file is a permanent source for reuse by this and future episodes covering the same chapter; a covered chapter never needs a live re-fetch of the source.
- `beat_id`/`maps_to_scene` line up with the numbering in `master-extract.json`/that episode's `01-master-narrative.json`, so Prompt Compiler can unambiguously pull the right detail for a given shot.

## Rules
- **The original source text is never stored verbatim in any repository file** (applies to both `master-extract.json` and `v<N>/c<M>-detailed.json`). The output is facts and short original phrasing, not paraphrased sentences that track the original's wording.
- The output must be substantially shorter than the source.
- **The goal of an onboarding pass is the entire currently-published work, volume by volume** — not an arbitrarily agreed-upon small chunk. Splitting into batches (e.g. one volume, or 10-15 chapters at a time) is a purely practical limit on source-site load (not sending one request across hundreds of chapters at once), not a reason to permanently stop after the first N chapters. If a work is very large or still ongoing, the human may deliberately narrow the scope ("only the volumes published so far, 1-3"), but that's an explicit human decision made up front, not a silent agent default.
- Requires the ability to read a web page (web fetch / browser tool, depending on which agent runs this skill); if the source is a JS-heavy site and a plain web fetch returns an empty/error page, use a browser tool that actually renders the page.
- **Gaps are filled automatically.** If a fact (e.g. a character's appearance) hasn't been described yet in the chapters read so far, Source Ingestion generates a plausible detail itself and flags it in `auto_generated_fields`, rather than stopping to ask. Rationale: early in a work it's unknown where a given detail will actually surface, so blocking the process on every unresolved field isn't worthwhile.
- The human gets a summary to confirm AFTER a batch completes (the overall picture of characters/world/plot), not one question per chapter.
- `adaptation_notes` are mandatory and specific — they're the basis of the post-batch confirmation checkpoint.
- Characters/locations from `characters_extracted` are handed to Registry Builder to create unlocked entries with `source_name` and `adapted_name`; fields flagged in `auto_generated_fields` may be overwritten by later chapters if the source provides more accurate information.
