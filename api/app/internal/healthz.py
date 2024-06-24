import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    '/api/v1/internal/healthz', response_class=HTMLResponse, tags=["工具", "Internal"]
)
async def health():
    """
    监控检测。
    """
    LOGGER.debug("healthz....")
    return ''
