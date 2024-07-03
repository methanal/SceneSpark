import pickle
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional

import aiofiles  # type: ignore[import]
from loguru import logger

# isort: off
from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

# isort: on
from fastapi.responses import ORJSONResponse, StreamingResponse

from app.bgtasks.bg_tasks import bg_llm_vision_clipper, bg_subtitle_clipper
from app.libs.config import settings
from utils.tools import purge_dir

# isort: off
# from clippers.prompt.prompt_text import (
#     PROMPT_PICK_IMG_RETURN_JSON,
#     PROMPT_PICK_SUBTITLE_RETURN_JSON,
# )

# isort: on

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=10)


@router.post(
    "/api/v1/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=ORJSONResponse,
)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(description="source video files."),  # noqa: B008
    request_id: Optional[str] = Form(None),  # noqa: B008
    subtitle_prompt: Optional[str] = Form(None),  # noqa: B008
    vision_prompt: Optional[str] = Form(None),  # noqa: B008
):
    logger.info("subtitle_prompt: {subtitle_prompt}", subtitle_prompt=subtitle_prompt)
    logger.info("vision_prompt: {vision_prompt}", vision_prompt=vision_prompt)

    output_dir = Path(f"{settings.UPLOAD_BASE_PATH}/{request_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    purge_dir(output_dir)
    logger.debug(f"vidoes path:{output_dir}")  # noqa: G004

    for f_in in files:
        fout_path = output_dir / f_in.filename  # type: ignore[operator]
        async with aiofiles.open(fout_path, 'wb') as f_out:
            while content := await f_in.read(1024 * 1024):
                await f_out.write(content)

        # subtitle_prompt = PROMPT_PICK_SUBTITLE_RETURN_JSON.format(
        #     selection_ratio=settings.LLM_SUBTITLE_SELECTION_RATIO
        # )
        background_tasks.add_task(
            executor.submit,
            bg_subtitle_clipper,
            video_path=fout_path,
            prompt=subtitle_prompt,
        )

        # vision_prompt = PROMPT_PICK_IMG_RETURN_JSON.format(
        #     selection_ratio=settings.LLM_VIDEO_SELECTION_RATIO
        # )
        background_tasks.add_task(
            bg_llm_vision_clipper, video_path=fout_path, prompt=vision_prompt
        )

    return {"message": "Files uploaded successfully", "request_id": request_id}


def load_pickle(request_id: str, suffix: str, pickle_name: str) -> list:
    mark_file = Path(f"{settings.UPLOAD_BASE_PATH}/{request_id}/clip_complete.{suffix}")
    pickle_file = Path(f"{settings.UPLOAD_BASE_PATH}/{request_id}/{pickle_name}.pkl")
    if mark_file.is_file() and mark_file.exists():
        with open(pickle_file, 'rb') as f:
            return pickle.load(f)  # nosec

    return []


@router.get(
    "/api/v1/extract/{request_id}/llm_srts",
    response_class=ORJSONResponse,
)
async def load_llm_srts(background_tasks: BackgroundTasks, request_id: str):
    if llm_srts := load_pickle(request_id, 'subtitle_clipper', 'llm_srts'):
        return {"msg": "done", "llm_srts": llm_srts}

    return {"msg": "not ready yet"}


@router.get(
    "/api/v1/extract/{request_id}/imgs_info",
    response_class=ORJSONResponse,
)
async def load_imgs_info(background_tasks: BackgroundTasks, request_id: str):
    if imgs_info := load_pickle(request_id, 'llm_vision_clipper', 'imgs_info'):
        return {"msg": "done", "imgs_info": imgs_info}

    return {"msg": "not ready yet"}


@router.get("/api/v1/download/{request_id}/{file_name}")
async def download_file(request_id: str, file_name: str):
    """
    TODO: This function currently serves no specific purpose,
    but is kept for potential use in future development.
    """
    file_path = Path(f"{settings.UPLOAD_BASE_PATH}/{request_id}/{file_name}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async def iterfile():
        async with aiofiles.open(file_path, mode="rb") as file_like:
            while content := await file_like.read(1024 * 1024):
                yield content

    return StreamingResponse(iterfile(), media_type="application/octet-stream")
