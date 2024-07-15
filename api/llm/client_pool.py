#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from itertools import cycle
from pathlib import Path

from loguru import logger
from ullm import LanguageModel

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from app.libs.config import settings  # noqa: E402


class OpenAIClientPool:
    _instance = None

    def __new__(cls, api_tokens):
        if cls._instance is None:
            cls._instance = super(OpenAIClientPool, cls).__new__(cls)
            cls._instance._init(api_tokens)
        return cls._instance

    def _init(self, api_tokens):
        self.api_tokens = api_tokens
        self.clients = []

        for token in self.api_tokens:
            config = {
                'type': 'remote',
                'model': 'gpt-4o',
                'provider': 'openai',
                'api_key': token,
                'temperature': settings.OPENAI_TEMPERATURE,
            }
            client = LanguageModel.from_config(config=config)
            self.clients.append(client)

        self.client_cycle = cycle(self.clients)

    def get_client(self):
        client = next(self.client_cycle)
        logger.debug("Using client with client: {client}", client=client)
        return client


if __name__ == "__main__":
    from llm.llm_wrapper import llm_tell_joke

    client_pool = OpenAIClientPool(api_tokens=settings.OPENAI_API_KEY_LIST)
    client = client_pool.get_client()
    joke = llm_tell_joke(client)
    logger.info("tell a joke: {joke}", joke=joke)
