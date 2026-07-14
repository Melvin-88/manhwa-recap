# Skill: Produce Episode

## Purpose
Orchestrates the full production pipeline for one episode: calls every skill agent in order, reads/writes episode files under the fixed numbering scheme, and pauses at human-confirmation checkpoints. This is the single command a human uses to run the whole process — not 8 separate commands.

**Precondition for a new story:** if `story-config.json` and `source-material/` don't yet exist for this `story_slug`, onboard first (Source Ingestion, section "Onboarding a New Story": fix the language(s) → fully collect the work by volume), and only then call Produce Episode for a specific episode. Produce Episode does not perform onboarding itself.

## Input
- `story_slug` (e.g. `example-story`) — determines which `stories/<story_slug>/` folder the whole call operates on
- `episode_id` (e.g. `ep02`)
- `stories/<story_slug>/episodes/<episode_id>/script.md` — the editorial brief: source URL(s), episode scope, deliberate changes
- `stories/<story_slug>/story-config.json` (`languages`, `default_language`) — the list of languages the audio branch and Assembly should run for; if the file is absent, assume `languages: ["uk"]`

All file paths below (`episodes/...`, `registries/...`, `characters/...`, `source-material/...`) are relative to the `stories/<story_slug>/` root, not the repository root. See `docs/architecture.md`, section "Structure for Multiple Stories".

## Output
No new data format — this skill only orchestrates calls to other skill agents in the order below and reads/writes the same numbered episode files defined in each skill's own Output section.

## Sequence

1. **Source Ingestion** → writes `episodes/<episode_id>/00-source-extract.json`
   → **CHECKPOINT 0**: show `adaptation_notes` to the human, wait for confirmation that the transformation is sufficient
2. **Registry Builder** (on-demand) → creates unlocked entries for new characters/locations in `registries/*.json`
   → **CHECKPOINT 2**: show the new entries, wait for the human to set `locked:true`
3. **Master Narrative** → writes `episodes/<episode_id>/01-master-narrative.json`
   → **CHECKPOINT 1**: show the scene breakdown, wait for confirmation
4. In parallel (independent branches, may run in either order):
   - **Visual branch**: Scene Intelligence Engine → `02-scene-intelligence.json` → Storyboard Planner → `03-storyboard.json` (calls Registry Builder on-demand if new locations/props appear) → Visual Shot Package → `04-visual-shot-package.json` → Prompt Compiler → `05-prompt-package.json`
     → **CHECKPOINT 3**: show the shot list and compiled prompts, wait for confirmation before spending generation calls
     → Image Director → `06-generation-log.json` (generates and downloads; `flagged_for_review` is provisional at this point)
     → Image QA → updates `06-generation-log.json` in place (judges every frame, regenerates up to 2 attempts itself if needed, sets the final `flagged_for_review`)
     → **CHECKPOINT 4**: only if entries with `flagged_for_review: true` remain after Image QA — show them and their `qa_notes` to the human, wait for a decision (manual prompt fix or accept as-is); if no such entries remain, skip this checkpoint and continue automatically
   - **Audio branch, separately for each language in `story-config.json.languages`**: Narrator/Audio Director → `audio/<lang>/02b-narration-script.json` → `audio/<lang>/generation-log.json` (flags `flagged_for_review` instead of silently generating). The visual branch (frames) is shared across all languages and generated only once.
5. **Assembly, separately for each language** (the mechanical script `scripts/assemble_episode.py --lang <lang>`, not an LLM call) → groups frames from `06-generation-log.json` by `scene_id` (via `03-storyboard.json`), for each scene splits that scene's audio duration evenly across its frames, renders each frame as its own video clip (a light Ken Burns zoom, audio mixed under it), and concatenates all clips into `episodes/<episode_id>/final/<episode_id>_<lang>.mp4`. Skips any entry with `flagged_for_review: true` (frame or audio) — never silently assembles a video with an unfixed defect. Each language is a fully separate exported file, not multi-track audio in one video.
   → **CHECKPOINT 5**: show the video(s), wait for a publish decision

## Rules
- Every step reads only the file(s) explicitly listed in that skill's own `Input` — it never "recalls" data from earlier conversation instead of reading the file.
- Pausing at a checkpoint means: show the human the concrete artifact (JSON/list/video) and wait, literally, for confirmation in chat before reading the next skill.
- If the human manually edits an intermediate file after a checkpoint (e.g. edits `01-master-narrative.json`), the next pipeline step reads the edited version, not the agent's original output.
- Any step can be rerun in isolation (e.g. "regenerate just `03-storyboard.json`") — that's simply calling the matching skill again with the same input file.
