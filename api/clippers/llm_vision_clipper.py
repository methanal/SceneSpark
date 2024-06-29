#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from typing import Dict, List

import cv2
import orjson
from loguru import logger

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from clippers.base_clipper import BaseClipper  # noqa: E402

# isort: off
from clippers.wrappers.llm_wrapper import (  # noqa: E402
    initialize_llm_client,
    llm_pick_imgs,
)

# isort: on


class LLMVisionClipper(BaseClipper):
    def __init__(self):
        super().__init__()
        self.llm_client = initialize_llm_client()

    def extract_clips(self, video_path: Path, prompt: str) -> List[Dict]:
        sample_interval = 2.0  # seconds
        encode_frames = LLMVisionClipper.sample_frames(
            video_path, interval=sample_interval, save_image=True
        )

        _imgs_json = llm_pick_imgs(self.llm_client, prompt, data_list=encode_frames)

        try:
            imgs_info = orjson.loads(_imgs_json)
        except orjson.JSONDecodeError as e:
            logger.warning("llm doesn't return JSON, it returns: %s", str(e))

        # FIXME: The following code has not been debugged
        raise NotImplementedError('Just Here')
        selected_frames = [int(s["index"]) - 1 for s in imgs_info]
        clip_metadata_list = self._store_clips(video_path, selected_frames)

        for metadata, s in zip(clip_metadata_list, imgs_info):
            metadata['extract'] = s['extract']

        return clip_metadata_list

    def _store_clips(self, video_path: Path, frames) -> List[Dict]:
        return list(dict())  # TODO

    @staticmethod
    def sample_frames(
        video_path: Path, interval: float = 5.0, save_image: bool = False
    ) -> List[str]:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)

        interval_frames = int(fps * interval)
        frame_count = 0
        encoded_frames = []

        while True:
            ret, frame = video.read()
            # _png_path = video_path.parent / f'{frame_count}.png'
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
                    _img_path = video_path.parent / f'{frame_count}.jpg'
                    with open(_img_path, "wb") as f:
                        f.write(_buffer.tobytes())

            frame_count += 1

        video.release()

        return encoded_frames


if __name__ == "__main__":
    from clippers.prompt.prompt_text import PROMPT_PICK_IMG_RETURN_JSON

    llmv_clipper = LLMVisionClipper()
    video_name = '2.mp4'

    llmv_clipper.extract_clips(
        video_path=Path(video_name), prompt=PROMPT_PICK_IMG_RETURN_JSON
    )
