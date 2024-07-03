# from loguru import logger

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.libs.config import settings

# isort: off
from clippers.prompt.prompt_text import (
    PROMPT_PICK_IMG_RETURN_JSON,
    PROMPT_PICK_SUBTITLE_RETURN_JSON,
)

# isort: on

router = APIRouter()


@router.get(
    "/api/v1/prompts/{request_id}",
    response_class=ORJSONResponse,
)
async def prompts(request_id: str):
    subtitle_prompt = PROMPT_PICK_SUBTITLE_RETURN_JSON.format(
        selection_ratio=settings.LLM_SUBTITLE_SELECTION_RATIO
    )
    video_prompt = PROMPT_PICK_IMG_RETURN_JSON.format(
        selection_ratio=settings.LLM_VIDEO_SELECTION_RATIO
    )
    return {'prompt1': subtitle_prompt, "prompt2": video_prompt}
