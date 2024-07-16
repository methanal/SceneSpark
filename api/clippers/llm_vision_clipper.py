import sys
from pathlib import Path
from typing import Optional

import orjson
from loguru import logger

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from app.libs.config import settings  # noqa: E402
from clippers.base_clipper import BaseClipper  # noqa: E402

# isort: off
from clippers.frame_sampler import (  # noqa: E402
    FrameSampler,
    subtitle_framer,
    time_framer,
)

# isort: on
from llm.llm_wrapper import llm_pick_imgs  # noqa: E402
from utils.tools import find_video_files  # noqa: E402


class LLMVisionClipper(BaseClipper):
    def __init__(
        self,
        upload_path: Path,
        sample_interval: float = 0.0,
        clip_duration: float = 0.0,
    ):
        super().__init__()
        self.upload_path = upload_path
        self.sample_interval = (
            sample_interval
            if sample_interval > 0.0
            else settings.VIDEO_SAMPLE_INTERVAL_SECOND
        )
        self.clip_duration = (
            clip_duration if clip_duration > 0.0 else settings.LLM_VISION_CLIP_DURATION
        )

    def extract_single_video_clips(
        self, llm_client, prompt: str, encode_frames: list, time_frames: list
    ) -> list:
        _imgs_json = llm_pick_imgs(
            llm_client,
            prompt,
            frames={'time_frames': time_frames, 'encode_frames': encode_frames},
        )
        logger.debug("llm vision resp raw:{_imgs_json}", _imgs_json=_imgs_json)
        try:
            imgs_info = orjson.loads(_imgs_json)
            imgs_info = imgs_info['picked']
        except orjson.JSONDecodeError as e:
            logger.warning("llm doesn't return JSON, it returns: %s", str(e))
            return []

        timeframe_imgs_info = []
        dup_start = set()
        for m in imgs_info:
            logger.debug("m: {m}", m=m)
            tf = time_frames[int(m['index'])]
            if (start := tf['start']) in dup_start:
                logger.info("same section: {}, {}", tf, m)
                continue

            dup_start.add(start)
            m['time_frame'] = tf
            m['start'] = start
            m['end'] = tf['end']
            timeframe_imgs_info.append(m)

        return timeframe_imgs_info

    def extract_clips(
        self,
        prompt: str,
        llm_client,
        sampler: FrameSampler = FrameSampler.TIME_BASE,
        subtitles: Optional[list] = None,
    ) -> dict[Path, list]:
        imgs_info_dict: dict[Path, list] = {}
        for video_file in find_video_files(self.upload_path):
            if sampler == FrameSampler.TIME_BASE:
                encode_frames, time_frames = time_framer(
                    video_file=video_file,
                    sample_interval=self.sample_interval,
                    clip_duration=self.clip_duration,
                )
            elif sampler == FrameSampler.SUBTITLE_BASE:
                encode_frames, time_frames = subtitle_framer(
                    video_file=video_file,
                    sample_interval=self.sample_interval,
                    clip_duration=self.clip_duration,
                    subtitles=subtitles,
                )

            if imgs_info := self.extract_single_video_clips(
                llm_client, prompt, encode_frames, time_frames
            ):
                imgs_info_dict[video_file] = imgs_info
            else:
                imgs_info_dict[video_file] = []

        return imgs_info_dict


if __name__ == "__main__":
    from llm.client_pool import OpenAIClientPool
    from prompt.prompt_text import PROMPT_PICK_IMG_RETURN_JSON

    client_pool = OpenAIClientPool(api_tokens=settings.OPENAI_API_KEY_LIST)
    # video_name = '2.mp4'
    llmv_clipper = LLMVisionClipper(upload_path=Path('.'))

    prompt = PROMPT_PICK_IMG_RETURN_JSON.format(
        selection_ratio=settings.LLM_VIDEO_SELECTION_RATIO
    )
    imgs_info_dict = llmv_clipper.extract_clips(
        prompt=prompt,
        llm_client=client_pool.get_client(),
        sampler=FrameSampler.TIME_BASE,
    )

    clips_path = Path('.')
    BaseClipper.store_clips(imgs_info_dict, clips_path)
    BaseClipper.pickle_segments_json(imgs_info_dict, clips_path, 'imgs_info_dict')
    imgs_info = BaseClipper.flatten_clips_result(imgs_info_dict)
