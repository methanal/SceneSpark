import logging
from pathlib import Path
from typing import List
import shutil

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/v1/upload")
async def upload_files(files: List[UploadFile] = File(...), text: str = Form(...)):
    LOGGER.warning(f"text:{text}")

    output_dir = Path("app/static/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    import pdb; pdb.set_trace()  # noqa

    for file in files:
        file_path = output_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    new_video_path = "static/videos/4.mp4"

    return JSONResponse(content={"video_url": f"{new_video_path}"})
