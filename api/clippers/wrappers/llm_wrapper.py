#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from pprint import pprint
from typing import Optional, Union

import orjson
from loguru import logger
from ullm import LanguageModel

parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(parent_dir))

from app.libs.config import settings  # noqa: E402


def initialize_llm_client(llm_provider: str = 'openai'):
    config = settings.get_llm_provider_config(provider=llm_provider)
    return LanguageModel.from_config(config=config)


def llm_pick_srts(llm_client, srts, prompt):
    messages = [
        {"role": "user", "content": f"{srts}"},
    ]
    response = llm_client.chat(messages, system=prompt)

    return response.content


def llm_pick_imgs(
    llm_client,
    prompt: str = '',
    image_list: Optional[list[str]] = None,
    frames: dict = None,
    time_frames: list = None,
    data_list: list = None,
):
    content: list[dict[str, Union[str, dict]]] = [{"type": "text", "text": prompt}]

    if image_list:
        content.extend({"type": "image", "path": img} for img in image_list)

    if frames:
        for encode_frame, time_frame in zip(
            frames['encode_frames'], frames['time_frames']
        ):
            if encode_frame:
                if srt := time_frame.get('srt'):
                    content.append({"type": "text", "text": srt})

                content.append({"type": "image", "data": encode_frame})

    messages = [{"role": "user", "content": content}]
    response = llm_client.chat(messages)

    if response.stop_reason == 'error':
        logger.warning(response)
        return {'picked': []}

    usage = orjson.loads(response.original_result)['usage']
    logger.info("LLM usage: {usage}", usage=usage)

    return response.content


if __name__ == "__main__":
    from clippers.prompt.prompt_text import PROMPT_IMGS_SUMMARY

    llm_client = initialize_llm_client()
    content = llm_pick_imgs(
        llm_client, PROMPT_IMGS_SUMMARY, image_list=['test1.png', 'test2.png']
    )
    pprint(content)
