"""
TODO: Refactor and merge this file into subtitle_clipper.py.

This file is planned to be refactored and incorporated into subtitle_clipper.py
to improve modularity and maintainability.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from moviepy import editor

LOGGER = logging.getLogger(__name__)


def concate_clips(args, path: Path, subs, result_filename: Optional[Path] = None):
    """
    Concatenate video clips based on subtitle segments.

    This function takes a video file and a list of subtitles, and creates a new
    video file that only includes the segments of the video corresponding to the subtitles.
    Segments of subtitles that are close together (within 0.5 seconds) are merged into a single segment.
    The resulting video is saved with the specified filename or with a "_cut" suffix added to the original filename.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, must include 'bitrate' attribute for video output.
    path : Path
        Path to the input video file.
    subs : list
        List of subtitle objects,
        each with 'start' and 'end' attributes indicating the start and end times of the subtitle.
    result_filename : Optional[Path], optional
        Path to save the resulting video file.
        If not provided, the result will be saved with a "_cut" suffix added to the original filename.

    Returns
    -------
    None

    Notes
    -----
    - The video segments are concatenated using the moviepy library.
    - The audio is normalized and the resulting video is saved with the 'aac' audio codec.
    - The function logs the reduction in video duration and the path to the saved media.

    Example
    -------
    >>> args = argparse.Namespace(bitrate="5000k")
    >>> path = Path("input_video.mp4")
    >>> subs = [
    ...     Subtitle(start=timedelta(seconds=10), end=timedelta(seconds=15)),
    ...     Subtitle(start=timedelta(seconds=20), end=timedelta(seconds=25)),
    ... ]
    >>> concate_clips(args, path, subs)
    Reduced duration from 30.0 to 10.0
    Saved media to input_video_cut.mp4
    """
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
    final_clip.write_videofile(
        result_filename.as_posix(), audio_codec="aac", bitrate=args.bitrate
    )

    media.close()
    logging.info(f"Saved media to {result_filename}")  # noqa: G004
