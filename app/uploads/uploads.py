import logging
from pathlib import Path
from typing import List
import shutil

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
# from fastapi.responses import StreamingResponse

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/v1/upload")
async def upload_files(files: List[UploadFile] = File(...), text: str = Form(...)):
    # TODO: upload 和 抽取 分成两个 button -->
    # TODO: 生成 form 的 UUID， upload 时创建文件夹，抽取时通过 UUID 定位文件夹. -->
    LOGGER.warning(f"text:{text}")

    output_dir = Path("app/static/videos")
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_path = output_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    new_video_path = "static/videos/4.mp4"

    return JSONResponse(content={"video_url": f"{new_video_path}"})

    # file_path = Path("static/videos/4.mp4")

    # def iterfile():
    #     with open(file_path, mode="rb") as file_like:
    #         yield from file_like

    # return StreamingResponse(iterfile(), media_type="video/mp4")
