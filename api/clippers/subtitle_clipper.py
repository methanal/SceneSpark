import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import orjson
import srt
from autocut.transcribe import Transcribe
from autocut.utils import load_audio
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
from utils.tools import find_video_files  # noqa: E402


class SubtitleClipper(BaseClipper):
    def __init__(self, autocut_args, upload_path: Path):
        super().__init__()
        self.autocut_args = autocut_args
        self.llm_client = initialize_llm_client()
        self.upload_path = upload_path

    def extract_clips(self, prompt: str) -> Dict[Path, list]:
        llm_srts_dict: Dict[Path, list] = {}
        for video_file in find_video_files(self.upload_path):
            self.autocut_args.inputs = [video_file]
            subs, srts = self.__transcribe_srt(video_file)
            _srts_json = llm_pick_srts(self.llm_client, srts, prompt)
            try:
                llm_srts = orjson.loads(_srts_json)
                llm_srts = llm_srts['picked']
            except orjson.JSONDecodeError as e:
                logger.warning("llm doesn't return JSON, it returns: {e}", e=str(e))
                llm_srts_dict[video_file] = []
                continue

            for s in llm_srts:
                sub = subs[int(s["index"]) - 1]
                s['start'] = sub.start.total_seconds()
                s['end'] = sub.end.total_seconds()
                s['subtitle'] = sub

            llm_srts_dict[video_file] = llm_srts

        return llm_srts_dict

    def __transcribe_srt(self, video_file: Path):
        transcriber = Transcribe(self.autocut_args)

        audio = load_audio(video_file, sr=transcriber.sampling_rate)
        speech_array_indices = transcriber._detect_voice_activity(audio)
        transcribe_results = transcriber._transcribe(
            video_file, audio, speech_array_indices
        )

        subs = transcriber.whisper_model.gen_srt(transcribe_results)
        srts = srt.compose(subs)
        logger.debug("{srts}", srts=srts)
        return subs, srts

    @staticmethod
    def gen_args(
        inputs: Optional[list] = None,
        audio_prompt: str = '',
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
            prompt=audio_prompt,
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

        logger.info("Saved merged video to {filename}", filename=merge_filename)


if __name__ == "__main__":
    from app.libs.config import settings
    from clippers.prompt.prompt_text import PROMPT_PICK_SUBTITLE_RETURN_JSON

    # video_name = '2.mp4'
    args = SubtitleClipper.gen_args()
    sub_clipper = SubtitleClipper(args, upload_path=Path('.'))

    prompt = PROMPT_PICK_SUBTITLE_RETURN_JSON.format(
        selection_ratio=settings.LLM_SUBTITLE_SELECTION_RATIO
    )
    llm_srts_dict = sub_clipper.extract_clips(prompt=prompt)

    clips_path = Path('.')
    BaseClipper.store_clips(llm_srts_dict, clips_path)
    BaseClipper.pickle_segments_json(llm_srts_dict, clips_path, 'llm_srts_dict')
    llm_srts = BaseClipper.flatten_clips_result(llm_srts_dict)
