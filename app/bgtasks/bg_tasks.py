import logging
from pathlib import Path
from typing import Optional

from clippers.subtitle_clipper import SubtitleClipper

LOGGER = logging.getLogger(__name__)


def bg_subtitle_clipper(
    video_path: Path, prompt: str, result_filename: Optional[Path] = None
):
    args = SubtitleClipper.gen_args()

    srt_clipper = SubtitleClipper(autocut_args=args)
    srt_clipper.extract_clips(video_path, prompt)

    # concate_clips(args, path, _subs, result_filename)  # Skip concatenation of clips.


def bg_llm_vision_clipper(
    path: Path, prompt: str, result_filename: Optional[Path] = None
):
    """
    Extracts key frames from a video,
    identifies important frames using LLM Vision,
    and returns the corresponding video segments and JSON descriptions.
    """
    ...


def bg_keyframe_clipper(
    path: Path, prompt: str, result_filename: Optional[Path] = None
):
    """
    References:
    -----------
    - https://github.com/joelibaceta/video-keyframe-detector
    - https://arxiv.org/abs/2401.04962
    """
    ...
