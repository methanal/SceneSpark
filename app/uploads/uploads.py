import logging
import shutil
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

from app.bgtasks.bg_tasks import auto_spark_clips

LOGGER = logging.getLogger(__name__)
router = APIRouter()


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
    output_dir = Path(f"app/static/videos/{request_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.debug(f"vidoes path:{output_dir}")  # noqa: G004

    for f_in in files:
        fout_path = output_dir / f_in.filename  # type: ignore[operator]
        async with aiofiles.open(fout_path, 'wb') as f_out:
            while content := await f_in.read(1024 * 1024):
                await f_out.write(content)

        background_tasks.add_task(auto_spark_clips, path=fout_path, prompt=prompt)

    return {"message": "Files uploaded successfully", "request_id": request_id}


@router.get(
    "/api/v1/extract/{request_id}",
    response_class=ORJSONResponse,
)
async def extract(request_id: str):
    # TODO
    """
    遍历 request_id 目录，找到 video 文件
        查找，确认 videos 都有对应的 videos_cut。否则循环等待。

    concatenate_videoclips 合并 videos_cut。
    抽取单视频函数。
    """

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
