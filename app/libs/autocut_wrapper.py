import argparse
import logging
from pathlib import Path
from typing import Dict, List

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


def concate_clips(args, path: Path, subs):
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

    # an alternative to birate is use crf, e.g. ffmpeg_params=['-crf', '18']
    output_fn = 'cut.mp4'  # FIXME
    final_clip.write_videofile(output_fn, audio_codec="aac", bitrate=args.bitrate)

    media.close()
    logging.info(f"Saved media to {output_fn}")  # noqa: G004
