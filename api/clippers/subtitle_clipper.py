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
    def __init__(self, autocut_args, video_path: Path):
        super().__init__()
        self.autocut_args = autocut_args
        self.llm_client = initialize_llm_client()
        self._video_path = video_path

    @property
    def video_path(self):
        return self._video_path

    def extract_clips(self, prompt: str) -> List[Dict]:
        self.autocut_args.inputs = [self.video_path]

        subs, srts = self.__transcribe_srt()

        _srts_json = llm_pick_srts(self.llm_client, srts, prompt)
        try:
            llm_srts = orjson.loads(_srts_json)
            llm_srts = llm_srts['picked']
        except orjson.JSONDecodeError as e:
            logger.warning("llm doesn't return JSON, it returns: {e}", e=str(e))
            return []

        for s in llm_srts:
            sub = subs[int(s["index"]) - 1]
            s['start'] = sub.start.total_seconds()
            s['end'] = sub.end.total_seconds()
            s['subtitle'] = sub

        if llm_srts:
            self.store_clips(llm_srts)
            self.pickle_segments_json(obj=llm_srts, name='llm_srts')
            self.mark_complete(suffix='subtitle_clipper')

        return llm_srts

    def __transcribe_srt(self):
        if not is_video(self.video_path):
            logger.warning(
                "{video_path} isn't a valid video.", video_path=self.video_path
            )

        transcriber = Transcribe(self.autocut_args)

        audio = load_audio(self.video_path, sr=transcriber.sampling_rate)
        speech_array_indices = transcriber._detect_voice_activity(audio)
        transcribe_results = transcriber._transcribe(
            self.video_path, audio, speech_array_indices
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

    video_name = '2.mp4'
    args = SubtitleClipper.gen_args()
    sub_clipper = SubtitleClipper(args, video_path=Path(video_name))
    prompt = PROMPT_PICK_SUBTITLE_RETURN_JSON.format(
        selection_ratio=settings.LLM_SUBTITLE_SELECTION_RATIO
    )

    sub_clipper.extract_clips(prompt=prompt)
