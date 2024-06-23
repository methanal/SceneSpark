#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import io
import logging
import time
from pathlib import Path
from typing import Dict, List

import cv2
import orjson
from PIL import Image

from clippers.base_clipper import BaseClipper
from clippers.wrappers.llm_wrapper import initialize_llm_client, llm_pick_imgs

LOGGER = logging.getLogger(__name__)


class LLMVisionClipper(BaseClipper):
    def __init__(self):
        super().__init__()
        self.llm_client = initialize_llm_client()

    def extract_clips(self, video_path: Path, prompt: str) -> List[Dict]:
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # encoded_img1 = encode_image('test1.png')
        # encoded_img2 = encode_image('test2.png')
        # encode_frames = [encoded_img1, encoded_img2]
        start_time_sample = time.monotonic()
        encode_frames = LLMVisionClipper.sample_frames(video_path, interval=5.0)
        end_time_sample = time.monotonic()
        LOGGER.debug(
            f"Sample Elapsed: {end_time_sample - start_time_sample}s"  # noqa: G004
        )

        _imgs_json = llm_pick_imgs(self.llm_client, prompt, data_list=encode_frames)
        end_time_llm = time.monotonic()
        LOGGER.debug(f"LLM Elapsed: {end_time_llm - end_time_sample}s")  # noqa: G004

        # FIXME: The following code has not been debugged
        imgs_info = orjson.loads(_imgs_json)
        selected_frames = [int(s["index"]) - 1 for s in imgs_info]
        clip_metadata_list = self._store_clips(video_path, selected_frames)

        for metadata, s in zip(clip_metadata_list, imgs_info):
            metadata['extract'] = s['extract']

        return clip_metadata_list

    def _store_clips(self, video_path: Path, frames) -> List[Dict]:
        return list(dict())  # TODO

    @staticmethod
    def sample_frames(video_path: Path, interval: float = 5.0) -> List[str]:
        video = cv2.VideoCapture(video_path)

        fps = video.get(cv2.CAP_PROP_FPS)

        interval_frames = int(fps * interval)
        frame_count = 0
        encoded_frames = []

        while True:
            ret, frame = video.read()

            if not ret:
                break

            if frame_count % interval_frames == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)

                buffered = io.BytesIO()
                pil_image.save(buffered, format="PNG")

                encoded_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
                encoded_frames.append(encoded_string)

                # Calculate the size of the original and encoded data
                original_size_bytes = len(
                    buffered.getvalue()
                )  # Size of original image data in bytes
                encoded_size_chars = len(
                    encoded_string
                )  # Size of encoded string in characters
                # Convert sizes to KB and MB
                original_size_kb = original_size_bytes / 1024
                original_size_mb = original_size_kb / 1024
                encoded_size_kb = encoded_size_chars / 1024
                encoded_size_mb = encoded_size_kb / 1024
                # Print sizes
                if original_size_mb >= 1:
                    LOGGER.debug(
                        f"Orig: {original_size_mb:.2f} MB, Encoded: {encoded_size_mb:.2f} MB"
                    )  # noqa: G004
                else:
                    LOGGER.debug(
                        f"Orig: {original_size_kb:.2f} KB, Encoded: {encoded_size_kb:.2f} KB"
                    )  # noqa: G004

            frame_count += 1

        video.release()

        return encoded_frames


if __name__ == "__main__":
    llmv_clipper = LLMVisionClipper()
    video_name = 'cut.mp4'
    prompt = "这几张图片描述了什么故事？"
    llmv_clipper.extract_clips(video_path=Path(video_name), prompt=prompt)
