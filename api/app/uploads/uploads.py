import pickle
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


@router.post(
    "/api/v1/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=ORJSONResponse,
)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(description="source video files."),  # noqa: B008
    request_id: Optional[str] = Form(None),  # noqa: B008
    prompt1: Optional[str] = Form(None),  # noqa: B008
    prompt2: Optional[str] = Form(None),  # noqa: B008
):
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
        subtitle_prompt = prompt1
        background_tasks.add_task(
            bg_subtitle_clipper, video_path=fout_path, prompt=subtitle_prompt
        )

        # video_prompt = PROMPT_PICK_IMG_RETURN_JSON.format(
        #     selection_ratio=settings.LLM_VIDEO_SELECTION_RATIO
        # )
        video_prompt = prompt2
        background_tasks.add_task(
            bg_llm_vision_clipper, video_path=fout_path, prompt=video_prompt
        )

    return {"message": "Files uploaded successfully", "request_id": request_id}


@router.get(
    "/api/v1/extract/{request_id}",
    response_class=ORJSONResponse,
)
async def extract(background_tasks: BackgroundTasks, request_id: str):
    resp = {"msg": "not ready yet"}

    def is_ready(suffix: str, pickle_name: str) -> bool:
        mark_file = Path(
            f"{settings.UPLOAD_BASE_PATH}/{request_id}/clip_complete.{suffix}"
        )
        pickle_file = Path(
            f"{settings.UPLOAD_BASE_PATH}/{request_id}/{pickle_name}.pkl"
        )
        if mark_file.is_file() and mark_file.exists():
            with open(pickle_file, 'rb') as f:
                llm_srts = pickle.load(f)  # nosec
                resp[pickle_name] = llm_srts
                return True

        return False

    if is_ready('subtitle_clipper', 'llm_srts') and is_ready(
        'llm_vision_clipper', 'imgs_info'
    ):
        resp["msg"] = "done"

    return resp


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
