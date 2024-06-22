#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import Dict, List, Optional, Union

from openai import OpenAI

from app.libs.config import settings

LOGGER = logging.getLogger(__name__)


def initialize_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)


def llm_pick_srts(llm_client, srts, prompt):
    response = llm_client.chat.completions.create(
        model='gpt-4o',  # "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{srts}"},
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content


def llm_pick_imgs(llm_client, encode_frames: Optional[List] = None, prompt: str = ''):
    content: List[Dict[str, Union[str, Dict]]] = [{"type": "text", "text": prompt}]
    for encoded_img in encode_frames:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_img}"},
            }
        )

    response = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        temperature=0.5,
    )

    LOGGER.warning(f"LLM usage: {response.usage}")  # noqa: G004
    print(response.choices[0])


if __name__ == "__main__":
    llm_client = initialize_openai_client()
    llm_pick_imgs(llm_client)
