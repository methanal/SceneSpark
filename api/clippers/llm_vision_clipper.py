#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
# import io
import logging
import time
import sys
from pathlib import Path
from typing import Dict, List

import cv2
import orjson
# from PIL import Image

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from clippers.base_clipper import BaseClipper  # noqa: E402
from clippers.wrappers.llm_wrapper import initialize_llm_client, llm_pick_imgs  # noqa: E402

LOGGER = logging.getLogger(__name__)


class LLMVisionClipper(BaseClipper):
    def __init__(self):
        super().__init__()
        self.llm_client = initialize_llm_client()

    def extract_clips(self, video_path: Path, prompt: str) -> List[Dict]:
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

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
    def sample_frames(video_path: Path, interval: float = 5.0, save_image: bool = False) -> List[str]:
        def _show_encoded_size(buffered_jpeg, encoded_string):
            _jpeg = len(buffered_jpeg.getvalue())
            _e = len(encoded_string)
            j_kb = _jpeg / 1024
            j_mb = j_kb / 1024
            e_kb = _e / 1024
            e_mb = e_kb / 1024
            if j_mb >= 1:
                print(f"jepg: {j_mb:.2f} MB, Encoded: {e_mb:.2f} MB")  # noqa: G004
            else:
                print(f"jepg: {j_kb:.2f} KB, Encoded: {e_kb:.2f} KB")  # noqa: G004

        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        interval_frames = int(fps * interval)
        frame_count = 0
        encoded_frames = []

        while True:
            ret, frame = video.read()
            if not ret:
                break

            # if frame_count % interval_frames == 0:
            #     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #     pil_image = Image.fromarray(frame_rgb)

            #     buffered_jpeg = io.BytesIO()
            #     pil_image.save(buffered_jpeg, format="JPEG", quality=65)

            #     encoded_string = base64.b64encode(buffered_jpeg.getvalue()).decode('utf-8')
            #     encoded_frames.append(encoded_string)

            #     _show_encoded_size(buffered_jpeg, encoded_string)

            #     if save_image:
            #         _img_path = video_path.parent / f'{frame_count}.png'
            #         with open(_img_path, "wb") as f:
            #             f.write(buffered_jpeg.getvalue())

            if frame_count % interval_frames == 0:
                ret, _buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                if not ret:
                    continue

                encoded_string = base64.b64encode(_buffer).decode('utf-8')
                encoded_frames.append(encoded_string)

                if save_image:
                    # _png_path = video_path.parent / f'{frame_count}.png'
                    # cv2.imwrite(_png_path, frame)
                    _img_path = video_path.parent / f'{frame_count}.jpg'
                    with open(_img_path, "wb") as f:
                        f.write(_buffer.getvalue())

            frame_count += 1

        video.release()

        return encoded_frames


if __name__ == "__main__":
    llmv_clipper = LLMVisionClipper()
    video_name = 'cut.mp4'
    prompt = "这几张图片描述了什么故事？"
    llmv_clipper.extract_clips(video_path=Path(video_name), prompt=prompt)
