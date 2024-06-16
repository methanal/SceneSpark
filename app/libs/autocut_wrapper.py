import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional

import srt
from autocut.transcribe import Transcribe
from autocut.utils import is_video, load_audio
from moviepy import editor

LOGGER = logging.getLogger(__name__)


def gen_args(
    inputs, prompt='', whisper_mode='whisper', whisper_model='small', device=None
):
    return argparse.Namespace(
        inputs=inputs,
        transcribe=None,
        cut=None,
        daemon=True,
        s=None,
        to_md=None,
        lang='zh',
        prompt=prompt,
        whisper_mode=whisper_mode,
        openai_rpm=3,
        whisper_model=whisper_model,
        bitrate='10m',
        vad='auto',
        force=None,
        encoding='utf-8',
        device=None,
    )


def transcribe_srt(args, path: Path):
    if not is_video(path):
        LOGGER.warning(f"{path} isn't a valid video.")  # noqa: G004

    transcriber = Transcribe(args)

    audio = load_audio(path, sr=transcriber.sampling_rate)
    speech_array_indices = transcriber._detect_voice_activity(audio)
    transcribe_results = transcriber._transcribe(path, audio, speech_array_indices)

    subs = transcriber.whisper_model.gen_srt(transcribe_results)
    srts = srt.compose(subs)
    LOGGER.debug(f"{srts}")  # noqa: G004
    return subs, srts


def concate_clips(args, path: Path, subs, result_filename: Optional[Path] = None):
    segments: List[Dict] = []

    subs.sort(key=lambda x: x.start)
    for x in subs:
        if len(segments) == 0:
            segments.append(
                {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
            )
        else:
            if x.start.total_seconds() - segments[-1]["end"] < 0.5:
                segments[-1]["end"] = x.end.total_seconds()
            else:
                segments.append(
                    {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                )

    media = editor.VideoFileClip(path.as_posix())

    clips = [media.subclip(s["start"], s["end"]) for s in segments]
    final_clip: editor.VideoClip = editor.concatenate_videoclips(clips)
    logging.info(
        f"Reduced duration from {media.duration:.1f} to {final_clip.duration:.1f}"  # noqa: G004
    )

    aud = final_clip.audio.set_fps(44100)
    final_clip = final_clip.without_audio().set_audio(aud)
    final_clip = final_clip.fx(editor.afx.audio_normalize)

    if not result_filename:
        result_filename = path.with_name(f"{path.stem}_cut.mp4")
    final_clip.write_videofile(result_filename, audio_codec="aac", bitrate=args.bitrate)

    media.close()
    logging.info(f"Saved media to {result_filename}")  # noqa: G004


def all_cut_ready(path: Path):
    """检查目录下，每个 {name}.{suffix}，都有对应的 {name}_cut.mp4 文件"""
    ret_files = []
    for file in path.iterdir():
        if is_video(file):
            cut_file = file.with_name(f"{file.stem}_cut.mp4")
            if not cut_file.exists():
                return []

            ret_files.append(cut_file)

    return ret_files


def merge_videos(cut_files: List[Path], session_path: Path):
    videos = []
    for file in cut_files:
        videos.append(editor.VideoFileClip(file.as_posix()))

    dur = sum([v.duration for v in videos])
    logging.info(f"Merging into a video with {dur / 60:.1f} min length")  # noqa: G004

    merged = editor.concatenate_videoclips(videos)

    fn = session_path.with_name("merge.mp4")
    args = gen_args(inputs=[])
    merged.write_videofile(fn, audio_codec="aac", bitrate=args.bitrate)

    logging.info(f"Saved merged video to {fn}")  # noqa: G004
    return fn
