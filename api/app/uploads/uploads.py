from typing import List, Optional

import aiofiles  # type: ignore[import]
from loguru import logger

# isort: off
from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    UploadFile,
    status,
)

# isort: on
from fastapi.responses import ORJSONResponse

from app.libs.config import settings
from utils.tools import ensure_dir

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
):
    upload_dir = ensure_dir(settings.UPLOAD_BASE_PATH, request_id)
    clips_dir = ensure_dir(settings.CLIPS_BASE_PATH, request_id)
    logger.debug(f"upload_dir: {upload_dir}, clips_dir: {clips_dir}")  # noqa: G004

    for f_in in files:
        fout_path = upload_dir / f_in.filename  # type: ignore[operator]
        async with aiofiles.open(fout_path, 'wb') as f_out:
            while content := await f_in.read(1024 * 1024):
                await f_out.write(content)

    return {"message": "Files uploaded.", "request_id": request_id}
