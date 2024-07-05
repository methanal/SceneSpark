import sys
from pathlib import Path
from typing import Dict, List

import cv2
import orjson
from loguru import logger

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from app.libs.config import settings  # noqa: E402
from clippers.base_clipper import BaseClipper  # noqa: E402

# isort: off
from clippers.wrappers.llm_wrapper import (  # noqa: E402
    initialize_llm_client,
    llm_pick_imgs,
)

# isort: on
from utils.tools import find_video_files  # noqa: E402


class LLMVisionClipper(BaseClipper):
    def __init__(self, upload_path: Path):
        super().__init__()
        self.llm_client = initialize_llm_client()
        self.upload_path = upload_path

    def extract_clips(self, prompt: str) -> List[Dict]:
        imgs_info_list = []
        for video_file in find_video_files(self.upload_path):
            video_file = video_file.resolve()

            sample_interval = settings.VIDEO_SAMPLE_INTERVAL_SECOND
            encode_frames = self.sample_frames(
                video_file=video_file, interval=sample_interval, save_image=True
            )
            _imgs_json = llm_pick_imgs(self.llm_client, prompt, data_list=encode_frames)
            logger.debug("llm vision resp raw:{_imgs_json}", _imgs_json=_imgs_json)
            try:
                imgs_info = orjson.loads(_imgs_json)
                imgs_info = imgs_info['picked']
            except orjson.JSONDecodeError as e:
                logger.warning("llm doesn't return JSON, it returns: %s", str(e))
                return []

            offset = sample_interval / 2
            for m in imgs_info:
                logger.debug("m: {m}", m=m)
                img_ts = int(m["index"]) * sample_interval  # image location (seconds)
                m['start'] = img_ts - offset
                m['end'] = img_ts + offset

            imgs_info_list.append({'source': video_file, 'segments': imgs_info})

        # TODO
        # The current editing approach results in poor audio continuity.
        # To fix this, use subtitle timing correction.
        return imgs_info

    def sample_frames(
        self, video_file: Path, interval: float = 5.0, save_image: bool = False
    ) -> List[str]:
        video = cv2.VideoCapture(video_file)
        fps = video.get(cv2.CAP_PROP_FPS)

        interval_frames = int(fps * interval)
        frame_count = 0
        encoded_frames = []

        while True:
            ret, frame = video.read()
            # _png_path = video_file.parent / f'{frame_count}.png'
            # cv2.imwrite(_png_path, frame)
            if not ret:
                break

            if frame_count % interval_frames == 0:
                ret, _buffer = cv2.imencode(
                    '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 45]
                )
                if not ret:
                    continue

                encoded_frames.append(_buffer.tobytes())

                if save_image:
                    _img_path = video_file.parent / f'{frame_count}.jpg'
                    with open(_img_path, "wb") as f:
                        f.write(_buffer.tobytes())

            frame_count += 1

        video.release()

        return encoded_frames


if __name__ == "__main__":
    from clippers.prompt.prompt_text import PROMPT_PICK_IMG_RETURN_JSON

    # video_name = '2.mp4'
    llmv_clipper = LLMVisionClipper(upload_path=Path('.'))

    prompt = PROMPT_PICK_IMG_RETURN_JSON.format(
        selection_ratio=settings.LLM_VIDEO_SELECTION_RATIO
    )
    imgs_info = llmv_clipper.extract_clips(prompt=prompt)

    clips_path = Path('.')
    BaseClipper.store_clips(imgs_info, clips_path)
    BaseClipper.pickle_segments_json(imgs_info, clips_path)
    imgs_info = BaseClipper.flatten_clips_result(imgs_info)
