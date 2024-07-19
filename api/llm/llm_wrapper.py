#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from pprint import pprint
from typing import Optional, Union

import orjson
from loguru import logger
from ullm import GenerateConfig

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from app.libs.config import settings  # noqa: E402


def get_generateconfig() -> GenerateConfig:
    # NOTE, If set max_*_tokens, you may got LLM_MAX_TOKENS_GPT4O completion.
    generate_config = {
        "temperature": settings.OPENAI_TEMPERATURE,
        "max_tokens": None,  # settings.LLM_MAX_TOKENS_GPT4O,
        "max_input_tokens": None,  # settings.LLM_MAX_TOKENS_GPT4O,
        "max_output_tokens": None,  # settings.LLM_MAX_TOKENS_GPT4O,
        "top_p": None,
        "top_k": None,
        "stop_sequences": None,
        "frequency_penalty": None,
        "presence_penalty": None,
        "repetition_penalty": None,
        "tools": None,
        "tool_choice": None,
    }
    return GenerateConfig(**generate_config)


def llm_pick_textlist(llm_client, textlist, prompt) -> str:
    messages = [
        {"role": "user", "content": f"{textlist}"},
    ]
    response = llm_client.chat(messages, system=prompt, config=get_generateconfig())

    return response.content


def llm_extract_imgs_info(
    llm_client, prompt: str, encode_frames: list, imgs_meta: Optional[list] = None
) -> list:
    imgs_info: list = []
    batch_size = settings.LLM_IMG_INFO_BATCH_SIZE
    for i in range(0, len(encode_frames), batch_size):
        content = [
            {"type": "image", "data": data}
            for data in encode_frames[i : i + batch_size]  # noqa: E203
        ]

        if imgs_meta:
            _meta = {
                "type": "text",
                "text": f"这里是视频的有时间轴的对白信息: {imgs_meta}",
            }
            content.append(_meta)

        messages = [{"role": "user", "content": content}]
        response = llm_client.chat(messages, system=prompt, config=get_generateconfig())

        if response.stop_reason in ['error', 'length']:
            logger.warning(response)
            imgs_info.extend([])

        try:
            _imgs_json = orjson.loads(response.content)
            imgs_info.extend(_imgs_json)
        except orjson.JSONDecodeError:
            logger.warning("llm doesn't return JSON, returns: {}", response.content)
            imgs_info.extend([])

    return imgs_info


def llm_pick_imgs(
    llm_client,
    prompt: str = '',
    image_list: Optional[list[str]] = None,
    frames: dict = None,
    time_frames: list = None,
    data_list: list = None,
):
    # content: list[dict[str, Union[str, dict]]] = [{"type": "text", "text": prompt}]
    content: list[dict[str, Union[str, dict]]] = []

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
    response = llm_client.chat(messages, system=prompt, config=get_generateconfig())

    if response.stop_reason == 'error':
        logger.warning(response)
        return {'picked': []}

    usage = orjson.loads(response.original_result)['usage']
    logger.info("LLM usage: {usage}", usage=usage)

    return response.content


def llm_tell_joke(
    llm_client, content: str = "Tell me a joke.", prompt: str = "You are joker."
) -> str:
    messages = [
        {"role": "user", "content": f"{content}"},
    ]
    response = llm_client.chat(messages, system=prompt, config=get_generateconfig())

    return response.content


if __name__ == "__main__":
    from llm.client_pool import OpenAIClientPool
    from prompt.prompt_text import PROMPT_IMGS_SUMMARY

    client_pool = OpenAIClientPool(api_tokens=settings.OPENAI_API_KEY_LIST)
    llm_client = client_pool.get_client()

    content = llm_pick_imgs(
        llm_client, PROMPT_IMGS_SUMMARY, image_list=['test1.png', 'test2.png']
    )
    pprint(content)
