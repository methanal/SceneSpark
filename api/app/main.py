from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.__version__ import __version__
from app.internal import healthz
from app.libs.config import settings
from app.prompts import prompts
from app.uploads import uploads
from utils.sentry import sentry_sdk  # noqa: F401

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthz.router)
app.include_router(uploads.router)
app.include_router(prompts.router)

app.mount("/videos", StaticFiles(directory=settings.UPLOAD_BASE_PATH), name="videos")

# @app.middleware("http")
# async def log_request_middleware(request: Request, call_next):
#     logger.debug(f"Request method: {request.method}")
#     logger.debug(f"Request url: {request.url}")
#
#     # To log the request body, we need to read it first
#     body = await request.body()
#     logger.debug(f"Request body: {body}")
#
#     response = await call_next(request)
#     return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the details of the request and the exception
    logger.error(f"Validation error: {exc}")
    logger.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )
