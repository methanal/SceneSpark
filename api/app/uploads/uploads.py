import logging
import uuid
from pathlib import Path
from typing import List

import aiofiles  # type: ignore[import]

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
from clippers.subtitle_clipper import SubtitleClipper

LOGGER = logging.getLogger(__name__)
router = APIRouter()
srt_prompts = {}


@router.post(
    "/api/v1/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=ORJSONResponse,
)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(description="source video files."),  # noqa: B008
    prompt: str = Form(...),  # noqa: B008
):
    LOGGER.debug(f"prompt:{prompt}")  # noqa: G004

    request_id = str(uuid.uuid4())
    srt_prompts[request_id] = prompt

    output_dir = Path(f"app/static/videos/{request_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.debug(f"vidoes path:{output_dir}")  # noqa: G004

    for f_in in files:
        fout_path = output_dir / f_in.filename  # type: ignore[operator]
        async with aiofiles.open(fout_path, 'wb') as f_out:
            while content := await f_in.read(1024 * 1024):
                await f_out.write(content)

        background_tasks.add_task(bg_subtitle_clipper, path=fout_path, prompt=prompt)
        background_tasks.add_task(bg_llm_vision_clipper, path=fout_path, prompt=prompt)

    return {"message": "Files uploaded successfully", "request_id": request_id}


@router.get(
    "/api/v1/extract/{request_id}",
    response_class=ORJSONResponse,
)
async def extract(background_tasks: BackgroundTasks, request_id: str):
    """
    TODO: Reimplement this function to extract clips and return each clip's JSON description.
    The JSON description should include tags and a brief description for each clip.

    Returns:
    list: A list of JSON objects, each representing a clip with tags and description.
    """
    session_path = Path(f"app/static/videos/{request_id}")

    if not (cut_files := SubtitleClipper.all_cut_ready(session_path)):
        return ORJSONResponse(
            content={"message": "cut still not ready yet"}, status_code=202
        )

    merge_filename = session_path / "merge.mp4"
    background_tasks.add_task(
        SubtitleClipper.merge_videos, cut_files, session_path, merge_filename
    )

    background_tasks.add_task(
        bg_subtitle_clipper,
        path=merge_filename,
        prompt=srt_prompts[request_id],
        result_filename=session_path / "final.mp4",
    )

    return {"message": "Extract job submitted"}


@router.get("/api/v1/download/{request_id}/{file_name}")
async def download_file(request_id: str, file_name: str):
    """
    TODO: This function currently serves no specific purpose,
    but is kept for potential use in future development.
    """
    file_path = Path(f"app/static/videos/{request_id}/{file_name}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async def iterfile():
        async with aiofiles.open(file_path, mode="rb") as file_like:
            while content := await file_like.read(1024 * 1024):
                yield content

    return StreamingResponse(iterfile(), media_type="application/octet-stream")
