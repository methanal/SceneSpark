import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import orjson
import srt
from autocut.transcribe import Transcribe
from autocut.utils import is_video, load_audio
from loguru import logger
from moviepy import editor

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from clippers.base_clipper import BaseClipper  # noqa: E402

# isort: off
from clippers.wrappers.llm_wrapper import (  # noqa: E402
    initialize_llm_client,
    llm_pick_srts,
)

# isort: on


class SubtitleClipper(BaseClipper):
    def __init__(self, autocut_args):
        super().__init__()
        self.autocut_args = autocut_args
        self.llm_client = initialize_llm_client()

    def extract_clips(self, video_path: Path, prompt: str) -> List[Dict]:
        self.autocut_args.inputs = [video_path]

        subs, srts = self.__transcribe_srt(video_path)

        _srts_json = llm_pick_srts(self.llm_client, srts, prompt)
        llm_srts = orjson.loads(_srts_json)
        llm_srts = llm_srts['picked']

        for s in llm_srts:
            sub = subs[int(s["index"]) - 1]
            s['start'] = sub.start.total_seconds()
            s['end'] = sub.end.total_seconds()

        self.store_clips(video_path, llm_srts)

        return llm_srts

    def __transcribe_srt(self, video_path: Path):
        if not is_video(video_path):
            logger.warning(f"{video_path} isn't a valid video.")  # noqa: G004

        transcriber = Transcribe(self.autocut_args)

        audio = load_audio(video_path, sr=transcriber.sampling_rate)
        speech_array_indices = transcriber._detect_voice_activity(audio)
        transcribe_results = transcriber._transcribe(
            video_path, audio, speech_array_indices
        )

        subs = transcriber.whisper_model.gen_srt(transcribe_results)
        srts = srt.compose(subs)
        logger.debug(f"{srts}")  # noqa: G004
        return subs, srts

    @staticmethod
    def gen_args(
        inputs: Optional[list] = None,
        prompt: str = '',
        whisper_mode: str = 'whisper',
        whisper_model: str = 'small',
        device: Optional[str] = None,
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

    @staticmethod
    def all_cut_ready(path: Path):
        """检查目录下，每个 {name}.{suffix}，都有对应的 {name}_cut.mp4 文件"""
        ret_files = []
        for file in path.iterdir():
            if is_video(file) and '_cut' not in file.stem:
                cut_file = file.with_name(f"{file.stem}_cut.mp4")
                if not cut_file.exists():
                    return []

                ret_files.append(cut_file)

        return ret_files

    @staticmethod
    def merge_videos(
        cut_files: List[Path], session_path: Path, merge_filename: Path, bitrate='10m'
    ):
        videos = []
        for file in cut_files:
            videos.append(editor.VideoFileClip(file.as_posix()))

        dur = sum([v.duration for v in videos])
        logger.info(
            f"Merging into a video with {dur / 60:.1f} min length"  # noqa: G004
        )

        merged = editor.concatenate_videoclips(videos)

        merged.write_videofile(
            merge_filename.as_posix(), audio_codec="aac", bitrate=bitrate
        )

        logger.info(f"Saved merged video to {merge_filename}")  # noqa: G004


if __name__ == "__main__":
    from clippers.prompt.prompt_text import PROMPT_PICK_SUBTITLE_RETURN_JSON

    args = SubtitleClipper.gen_args()
    sub_clipper = SubtitleClipper(args)
    video_name = '2.mp4'

    sub_clipper.extract_clips(
        video_path=Path(video_name), prompt=PROMPT_PICK_SUBTITLE_RETURN_JSON
    )
