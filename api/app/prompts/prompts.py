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
    PROMPT_IMAGE_META_DESCRIPTION_SUBTITLE,
    PROMPT_IMAGE_META_TAG_SCORE,
    PROMPT_PICK_VIDEO_META,
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
    img_meta_desc_subs = PROMPT_IMAGE_META_DESCRIPTION_SUBTITLE
    img_meta_tag_score = PROMPT_IMAGE_META_TAG_SCORE
    video_meta_prompt = PROMPT_PICK_VIDEO_META
    return {
        'subtitle_prompt': subtitle_prompt,
        "vision_prompt": vision_prompt,
        "whisper_prompt": whisper_prompt,
        "vision_with_srt_prompt": vision_with_srt_prompt,
        "img_meta_desc_subs": img_meta_desc_subs,
        "img_meta_tag_score": img_meta_tag_score,
        "video_meta_prompt": video_meta_prompt,
    }
