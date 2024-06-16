import logging
import shutil
import uuid
from pathlib import Path
from typing import List

import aiofiles  # type: ignore[import]
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import ORJSONResponse, StreamingResponse

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/api/v1/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=ORJSONResponse,
)
async def upload_files(
    files: List[UploadFile] = File(description="source video files."),  # noqa: B008
    text: str = Form(...),  # noqa: B008
):
    LOGGER.warning(f"text:{text}")  # noqa: G004

    request_id = str(uuid.uuid4())
    output_dir = Path(f"app/static/videos/{request_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.warning(f"vidoes path:{output_dir}")  # noqa: G004

    for f_in in files:
        fi_path = output_dir / f_in.filename  # type: ignore[operator]
        async with aiofiles.open(fi_path, 'wb') as f_out:
            while content := await f_in.read(1024 * 1024):
                await f_out.write(content)

    # return JSONResponse(content={"video_url": f"{new_video_path}"})
    return {"message": "Files uploaded successfully", "request_id": request_id}


@router.get(
    "/api/v1/extract/{request_id}",
    response_class=ORJSONResponse,
)
async def extract(request_id: str):
    from_path = Path("app/static/videos/5.mp4")
    to_folder = Path(f"app/static/videos/{request_id}")
    to_path = to_folder / "cut.mp4"

    to_folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(from_path, to_path)

    return {"message": "Extract successfully"}


@router.get("/api/v1/download/{request_id}/{file_name}")
async def download_file(request_id: str, file_name: str):
    # TODO
    file_path = Path(f"app/static/videos/{request_id}/{file_name}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async def iterfile():
        async with aiofiles.open(file_path, mode="rb") as file_like:
            while content := await file_like.read(1024 * 1024):
                yield content

    return StreamingResponse(iterfile(), media_type="application/octet-stream")
