# from loguru import logger

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.libs.config import settings

# isort: off
from prompt.prompt_text import (
    PROMPT_PICK_IMG_RETURN_JSON,
    PROMPT_PICK_SUBTITLE_RETURN_JSON,
    PROMPT_WHISPER,
    PROMPT_PICK_VIDEO_META_RETURN_JSON,
    # PROMPT_PICK_VIDEO_META_ALL_RETURN_JSON,
    # PROMPT_PICK_VIDEO_META_ALL_STEP1_RETURN_JSON,
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
    vision_prompt = PROMPT_PICK_IMG_RETURN_JSON.format(
        selection_ratio=settings.LLM_VIDEO_SELECTION_RATIO
    )
    whisper_prompt = PROMPT_WHISPER
    vision_with_srt_prompt = PROMPT_PICK_VIDEO_META_RETURN_JSON
    # vision_with_srt_prompt = PROMPT_PICK_VIDEO_META_ALL_RETURN_JSON
    # vision_with_srt_prompt = PROMPT_PICK_VIDEO_META_ALL_STEP1_RETURN_JSON
    return {
        'subtitle_prompt': subtitle_prompt,
        "vision_prompt": vision_prompt,
        "whisper_prompt": whisper_prompt,
        "vision_with_srt_prompt": vision_with_srt_prompt,
    }
