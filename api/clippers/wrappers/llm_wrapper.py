#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from pprint import pprint
from typing import Dict, List, Optional, Union

import orjson
from ullm import LanguageModel

from app.libs.config import settings

LOGGER = logging.getLogger(__name__)


def initialize_llm_client(llm_provider: str = 'openai'):
    config = settings.get_llm_provider_config(provider=llm_provider)
    return LanguageModel.from_config(config=config)


def llm_pick_srts(llm_client, srts, prompt):
    messages = [
        {"role": "system", "content": f"{prompt}"},
        {"role": "user", "content": f"{srts}"},
    ]
    response = llm_client.chat(messages)

    return response.content


def llm_pick_imgs(
    llm_client,
    prompt: str = '',
    image_list: Optional[List[str]] = None,
    data_list: List = None,
):
    content: List[Dict[str, Union[str, Dict]]] = [{"type": "text", "text": prompt}]

    if image_list:
        content.extend({"type": "image", "path": img} for img in image_list)

    if data_list:
        content.extend({"type": "image", "data": data} for data in image_list)

    messages = [{"role": "user", "content": content}]
    response = llm_client.chat(messages)

    usage = orjson.loads(response.original_result)['usage']
    LOGGER.warning(f"LLM usage: {usage}")  # noqa: G004

    return response.content


if __name__ == "__main__":
    prompt = "这几张图片描述了什么故事？"
    llm_client = initialize_llm_client()

    content = llm_pick_imgs(llm_client, prompt, image_list=['test1.png', 'test2.png'])
    pprint(content)
