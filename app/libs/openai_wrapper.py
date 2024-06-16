import logging

from openai import OpenAI

from app.libs.config import settings

LOGGER = logging.getLogger(__name__)


def pick_srts(srts, prompt):
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    response = client.chat.completions.create(
        model='gpt-4o',  # "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{srts}"},
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content
