#!/usr/bin/env python3
"""Assembly step from produce-episode/SKILL.md: combines Image QA-approved shots
and narrator audio into per-scene video clips, then concatenates them into one episode file.

Visuals are shared across languages; audio/text/output are per-language (audio/<lang>/,
final/<episode_id>_<lang>.mp4) per story-config.json.languages.

Usage:
    python3 scripts/assemble_episode.py <story_slug> <episode_id> --lang uk [--shots SHOT_001,SHOT_002,...] [--out NAME.mp4]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESOLUTION = (1920, 1080)
ZOOM_END = 1.08


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def build_shot_clip(image_path: Path, audio_path: Path, start: float, duration: float, out_path: Path):
    """One shot -> one clip: looped image with subtle Ken Burns zoom, muxed with its audio slice."""
    w, h = RESOLUTION
    frames = max(int(round(duration * 25)), 1)
    zoom_expr = f"1+({ZOOM_END}-1)*on/{frames}"
    vf = (
        f"scale={w*2}:{h*2},"
        f"zoompan=z='{zoom_expr}':d={frames}:s={w}x{h}:fps=25,"
        f"format=yuv420p"
    )
    audio_args = ["-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(audio_path)]
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        *audio_args,
        "-vf", vf, "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("story_slug")
    parser.add_argument("episode_id")
    parser.add_argument("--lang", required=True, help="Language code matching audio/<lang>/ and story-config.json.languages")
    parser.add_argument("--shots", help="Comma-separated shot_id whitelist for a partial/test run")
    parser.add_argument("--out", default=None, help="Output filename under final/ (default: <episode_id>_<lang>.mp4)")
    args = parser.parse_args()

    story_dir = ROOT / "stories" / args.story_slug
    story_config = load_json(story_dir / "story-config.json") if (story_dir / "story-config.json").exists() else {"languages": ["uk"]}
    if args.lang not in story_config["languages"]:
        sys.exit(f"'{args.lang}' is not in story-config.json languages {story_config['languages']}")

    ep_dir = story_dir / "episodes" / args.episode_id
    storyboard = load_json(ep_dir / "03-storyboard.json")["shots"]
    gen_log = {a["shot_id"]: a for a in load_json(ep_dir / "06-generation-log.json")["generated_assets"]}
    audio_log = {a["scene_id"]: a for a in load_json(ep_dir / "audio" / args.lang / "generation-log.json")["generated_assets"]}

    shot_whitelist = set(args.shots.split(",")) if args.shots else None

    # Group shots by scene_id, preserving storyboard order.
    scenes_order = []
    scene_shots = {}
    for shot in storyboard:
        shot_id, scene_id = shot["shot_id"], shot["scene_id"]
        if shot_whitelist and shot_id not in shot_whitelist:
            continue
        if shot_id not in gen_log or scene_id not in audio_log:
            continue
        if gen_log[shot_id].get("flagged_for_review") or audio_log[scene_id].get("flagged_for_review"):
            print(f"skip {shot_id}: flagged_for_review", file=sys.stderr)
            continue
        if scene_id not in scene_shots:
            scene_shots[scene_id] = []
            scenes_order.append(scene_id)
        scene_shots[scene_id].append(shot_id)

    clips_dir = ep_dir / "final" / "clips" / args.lang
    clips_dir.mkdir(parents=True, exist_ok=True)
    clip_paths = []

    for scene_id in scenes_order:
        shot_ids = scene_shots[scene_id]
        audio_path = story_dir / audio_log[scene_id]["audio_path"]
        total_duration = ffprobe_duration(audio_path)
        per_shot = total_duration / len(shot_ids)

        for i, shot_id in enumerate(shot_ids):
            image_path = story_dir / gen_log[shot_id]["asset_path"]
            out_clip = clips_dir / f"{shot_id}.mp4"
            build_shot_clip(image_path, audio_path, start=i * per_shot, duration=per_shot, out_path=out_clip)
            clip_paths.append(out_clip)
            print(f"built {out_clip.relative_to(ROOT)} ({per_shot:.2f}s)")

    concat_list = clips_dir / "_concat.txt"
    concat_list.write_text("".join(f"file '{p.resolve()}'\n" for p in clip_paths), encoding="utf-8")

    out_name = args.out or f"{args.episode_id}_{args.lang}.mp4"
    final_out = ep_dir / "final" / out_name
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c", "copy", str(final_out)],
        check=True, capture_output=True,
    )
    print(f"\nfinal video: {final_out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
