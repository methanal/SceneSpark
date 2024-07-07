from pathlib import Path

import aiofiles  # type: ignore[import]
from loguru import logger

# isort: off
from fastapi import (
    APIRouter,
    HTTPException,
)

# isort: on
from fastapi.responses import ORJSONResponse, StreamingResponse

# isort: off
from app.clips.schemas import (
    LLMVisionClipperRequest,
    MergeJsonRequest,
    SubtitleClipperRequest,
)

# isort: on
from app.libs.config import settings
from clippers.base_clipper import BaseClipper
from clippers.llm_vision_clipper import LLMVisionClipper
from clippers.subtitle_clipper import SubtitleClipper
from utils.tools import ensure_dir, load_pickle

router = APIRouter()


@router.post(
    "/api/v1/clips/extract/llm_srts",
    response_class=ORJSONResponse,
)
async def load_llm_srts(request: SubtitleClipperRequest):
    logger.info(f"subtitle clipper request: {request.json()}")  # noqa: G004

    args = SubtitleClipper.gen_args(
        whisper_mode=request.translation_model, whisper_model=request.model_size
    )
    upload_path = ensure_dir(settings.UPLOAD_BASE_PATH, request.request_id)
    srt_clipper = SubtitleClipper(autocut_args=args, upload_path=upload_path)
    llm_srts_dict = srt_clipper.extract_clips(prompt=request.prompt)

    if not llm_srts_dict:
        raise HTTPException(status_code=404, detail="No clips found")

    clips_path = ensure_dir(settings.CLIPS_BASE_PATH, request.request_id)
    BaseClipper.store_clips(llm_srts_dict, clips_path)
    BaseClipper.pickle_segments_json(llm_srts_dict, clips_path, 'llm_srts_dict')
    llm_srts = BaseClipper.flatten_clips_result(llm_srts_dict)

    return {"llm_srts": llm_srts}


@router.post(
    "/api/v1/clips/extract/imgs_info",
    response_class=ORJSONResponse,
)
async def load_imgs_info(request: LLMVisionClipperRequest):
    logger.info(f"llm_vision clipper request: {request.json()}")  # noqa: G004

    upload_path = ensure_dir(settings.UPLOAD_BASE_PATH, request.request_id)
    llmv_clipper = LLMVisionClipper(
        upload_path, request.sample_interval, request.clip_duration
    )
    imgs_info_dict = llmv_clipper.extract_clips(prompt=request.prompt)

    if not imgs_info_dict:
        raise HTTPException(status_code=404, detail="No clips found")

    clips_path = ensure_dir(settings.CLIPS_BASE_PATH, request.request_id)
    BaseClipper.store_clips(imgs_info_dict, clips_path)
    BaseClipper.pickle_segments_json(imgs_info_dict, clips_path, 'imgs_info_dict')
    imgs_info = BaseClipper.flatten_clips_result(imgs_info_dict)

    return {"imgs_info": imgs_info}


@router.post(
    "/api/v1/clips/merge_json",
    response_class=ORJSONResponse,
)
async def load_merge_json(request: MergeJsonRequest):
    logger.info(f"merge json request: {request.json()}")  # noqa: G004

    llm_srts_dict = load_pickle(request.request_id, 'llm_srts_dict')
    imgs_info_dict = load_pickle(request.request_id, 'imgs_info_dict')

    if not llm_srts_dict:
        merge_json = (
            BaseClipper.flatten_clips_result(imgs_info_dict) if imgs_info_dict else []
        )
        return {"merge_json": merge_json}
    if not imgs_info_dict:
        merge_json = (
            BaseClipper.flatten_clips_result(llm_srts_dict) if llm_srts_dict else []
        )
        return {"merge_json": merge_json}

    merge_json_dict = BaseClipper.merge_clips_dict(llm_srts_dict, imgs_info_dict)
    clips_path = ensure_dir(settings.CLIPS_BASE_PATH, request.request_id)
    BaseClipper.store_clips(merge_json_dict, clips_path)
    merge_json = BaseClipper.flatten_clips_result(merge_json_dict)

    return {"merge_json": merge_json}


@router.get("/api/v1/clips/download/{file_name}")
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
