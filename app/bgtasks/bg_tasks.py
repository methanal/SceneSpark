import logging
from pathlib import Path
from typing import Optional

from app.libs.autocut_wrapper import concate_clips, gen_args, transcribe_srt
from app.libs.openai_wrapper import pick_srts

LOGGER = logging.getLogger(__name__)


def auto_spark_clips(path: Path, prompt: str, result_filename: Optional[Path] = None):
    args = gen_args(inputs=[path])

    subs, srts = transcribe_srt(args, path)

    _srts = pick_srts(srts, prompt)
    idx = [int(s) - 1 for s in _srts.split('\n') if s]

    _subs = [subs[i] for i in idx]
    concate_clips(args, path, _subs, result_filename)

    """
    video clips 按 时间线 拼接, concatenate_videoclips
    write_videofile，重命名 video<i>_clips.mp4"""
