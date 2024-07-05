from pathlib import Path
from typing import Optional

import aiofiles  # type: ignore[import]
from loguru import logger

# isort: off
from fastapi import (
    APIRouter,
    Form,
    HTTPException,
)

# isort: on
from fastapi.responses import ORJSONResponse, StreamingResponse

from app.libs.config import settings
from clippers.base_clipper import BaseClipper
from clippers.llm_vision_clipper import LLMVisionClipper
from clippers.subtitle_clipper import SubtitleClipper
from utils.tools import ensure_dir

router = APIRouter()


@router.post(
    "/api/v1/clips/extract/{request_id}/llm_srts",
    response_class=ORJSONResponse,
)
async def load_llm_srts(
    request_id: Optional[str] = Form(None),  # noqa: B008
    prompt: Optional[str] = Form(None),  # noqa: B008
):
    logger.info(f"subtitle_prompt: {prompt}")  # noqa: G004

    args = SubtitleClipper.gen_args()
    upload_path = ensure_dir(settings.UPLOAD_BASE_PATH, request_id)
    srt_clipper = SubtitleClipper(autocut_args=args, upload_path=upload_path)
    llm_srts = srt_clipper.extract_clips(prompt=prompt)

    clips_path = ensure_dir(settings.CLIPS_BASE_PATH, request_id)
    BaseClipper.store_clips(llm_srts, clips_path)
    BaseClipper.pickle_segments_json(llm_srts, clips_path)
    BaseClipper.flatten_clips_result(llm_srts)

    return {"llm_srts": llm_srts}


@router.post(
    "/api/v1/clips/extract/{request_id}/imgs_info",
    response_class=ORJSONResponse,
)
async def load_imgs_info(
    request_id: Optional[str] = Form(None),  # noqa: B008
    prompt: Optional[str] = Form(None),  # noqa: B008
):
    logger.info(f"vision_prompt: {prompt}")  # noqa: G004

    upload_path = ensure_dir(settings.UPLOAD_BASE_PATH, request_id)
    llmv_clipper = LLMVisionClipper(upload_path)
    imgs_info = llmv_clipper.extract_clips(prompt=prompt)

    clips_path = ensure_dir(settings.CLIPS_BASE_PATH, request_id)
    BaseClipper.store_clips(imgs_info, clips_path)
    BaseClipper.pickle_segments_json(imgs_info, clips_path)
    BaseClipper.flatten_clips_result(imgs_info)

    return {"imgs_info": imgs_info}


@router.get("/api/v1/clips/download/{request_id}/{file_name}")
async def download_file(request_id: str, file_name: str):
    """
    TODO: This function currently serves no specific purpose,
    but is kept for potential use in future development.
    """
    file_path = Path(f"{settings.CLIPS_BASE_PATH}/{request_id}/{file_name}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async def iterfile():
        async with aiofiles.open(file_path, mode="rb") as file_like:
            while content := await file_like.read(1024 * 1024):
                yield content

    return StreamingResponse(iterfile(), media_type="application/octet-stream")
