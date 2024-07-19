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
from llm.client_pool import OpenAIClientPool  # noqa: E402
from llm.llm_wrapper import (  # noqa: E402
    llm_extract_imgs_info,
    llm_pick_imgs,
    llm_pick_textlist,
)

# isort: on
from utils.tools import find_video_files  # noqa: E402

client_pool = OpenAIClientPool(api_tokens=settings.OPENAI_API_KEY_LIST)


def _merge_desc_sub_entries(imgs_desc_sub: list, time_frames: list) -> list:
    merged_data = []
    current_entry = None
    first_index = None

    for item in imgs_desc_sub:
        if current_entry is None:
            first_index = item['index']
            current_entry = {
                "index": f"{first_index}",
                "description": [item["description"]],  # merge description
                "frame_subtitle": [item["subtitle"]],  # merge frame_subtitle
                "start": time_frames[first_index]['start'],
                "end": time_frames[first_index]['end'],
                'audio_subtitle': [
                    time_frames[first_index]['srt']
                ],  # merge audio_subtitle
            }
        elif (
            item["subtitle"] == current_entry["frame_subtitle"]
            and item['audio_subtitle'] == current_entry['audio_subtitle']
        ):
            # NOTE: Using both frame_subtitle and audio_subtitle extracts more segments
            current_entry["index"] = f"{first_index}-{item['index']}"
            current_entry['end'] = time_frames[item['index']]['end']
            if item["description"] not in current_entry["description"]:
                current_entry["description"].append(item["description"])
            if item["subtitle"] not in current_entry["frame_subtitle"]:
                current_entry["frame_subtitle"].append(item["subtitle"])
            if item["audio_subtitle"] not in current_entry["audio_subtitle"]:
                current_entry["audio_subtitle"].append(item["audio_subtitle"])
        else:
            current_entry["description"] = ' '.join(current_entry["description"])
            current_entry["frame_subtitle"] = ' '.join(
                [x for x in current_entry["frame_subtitle"] if x]
            )
            current_entry["audio_subtitle"] = ' '.join(
                [x for x in current_entry["audio_subtitle"] if x]
            )
            merged_data.append(current_entry)

            first_index = item['index']
            current_entry = {
                "index": f"{first_index}",
                "description": [item["description"]],
                "frame_subtitle": [item["subtitle"]],
                "start": time_frames[first_index]['start'],
                "end": time_frames[first_index]['end'],
                'audio_subtitle': [time_frames[first_index]['srt']],
            }

    if current_entry is not None:
        current_entry["description"] = ' '.join(current_entry["description"])
        current_entry["frame_subtitle"] = ' '.join(
            [x for x in current_entry["frame_subtitle"] if x]
        )
        current_entry["audio_subtitle"] = ' '.join(
            [x for x in current_entry["audio_subtitle"] if x]
        )
        merged_data.append(current_entry)

    return merged_data


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

    def extract_imgs_meta(
        self,
        llm_client,
        encode_frames: list,
        time_frames: list,
        prompt_frame_desc_subs: str,
        prompt_frame_tag_score: str,
        prompt_video_meta: str,
    ) -> list:
        imgs_desc_sub = llm_extract_imgs_info(
            llm_client=client_pool.get_client(),
            prompt=prompt_frame_desc_subs,  # PROMPT_IMAGE_META_DESCRIPTION_SUBTITLE
            encode_frames=encode_frames,
        )
        logger.debug("llm extract imgs_desc_sub, resp:{}", imgs_desc_sub)
        if not imgs_desc_sub:
            return []
        BaseClipper.pickle_segments_json(
            imgs_desc_sub, self.upload_path, 'imgs_desc_sub'
        )

        merged_imgs_desc_sub = _merge_desc_sub_entries(imgs_desc_sub, time_frames)

        # FIXME, Due to TPM limits. A rate limiter should be implemented later.
        # logger.warning("Sleeping 60s...")
        # sleep(60)
        imgs_meta = llm_extract_imgs_info(
            llm_client=client_pool.get_client(),
            prompt=prompt_frame_tag_score,  # PROMPT_IMAGE_META_TAG_SCORE
            encode_frames=encode_frames,
            imgs_meta=merged_imgs_desc_sub,
        )
        logger.debug("llm extract imgs_meta, resp:{}", imgs_meta)
        if not imgs_meta:
            return []
        BaseClipper.pickle_segments_json(imgs_meta, self.upload_path, 'imgs_meta')

        # FIXME, Due to TPM limits. A rate limiter should be implemented later.
        # logger.warning("Sleeping 60s...")
        # sleep(60)
        _imgs_picked = llm_pick_textlist(
            llm_client=client_pool.get_client(),
            textlist=imgs_meta,
            prompt=prompt_video_meta,  # PROMPT_PICK_VIDEO_META
        )
        try:
            imgs_picked = orjson.loads(_imgs_picked)
            imgs_picked = imgs_picked['picked']

            logger.debug("llm extract imgs_picked, resp:{}", imgs_picked)
            BaseClipper.pickle_segments_json(
                imgs_picked, self.upload_path, 'imgs_picked'
            )
            return imgs_picked
        except orjson.JSONDecodeError:
            logger.warning("llm_pick_textlist doesn't return JSON, {}", _imgs_picked)
            return []

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
        except orjson.JSONDecodeError:
            logger.warning("llm doesn't return JSON, it returns: {}", _imgs_json)
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
