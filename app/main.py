import logging
import logging.config

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.__version__ import __version__
from app.internal import healthz
from app.libs.config import settings
from app.uploads import uploads

from utils.sentry import sentry_sdk  # noqa: F401

logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger(__name__)

description = """
# SceneSpark
"""

app = FastAPI(
    title="SceneSpark",
    description=description,
    version=__version__,
    contact={
        "name": "Peng Wang",
        "email": "hi@buqi.io",
    },
    redoc_url=None,
)
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(healthz.router)
app.include_router(uploads.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("app/static/index.html") as f:
        return HTMLResponse(content=f.read())
