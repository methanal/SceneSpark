import logging

import httpx
from fastapi import HTTPException
from pydantic import Json

LOGGER = logging.getLogger(__name__)


async def http_get(url: str, params: dict = {}) -> Json:
    transport = httpx.AsyncHTTPTransport(retries=1)
    async with httpx.AsyncClient(transport=transport, timeout=20) as client:
        try:
            response = await client.get(url, params=params, timeout=1)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            LOGGER.warning("An error occurred while requesting %s.", exc.request.url)
            raise HTTPException(status_code=500, detail=str(exc))
        except httpx.HTTPStatusError as exc:
            status_error_code = exc.response.status_code
            LOGGER.warning(
                "Error response %s while requesting %s.",
                status_error_code,
                exc.request.url,
            )
            raise HTTPException(status_code=status_error_code, detail=exc.response.text)


async def http_post(url: str, payload: dict = {}) -> Json:
    LOGGER.warning("ready to post:%s", payload)
    transport = httpx.AsyncHTTPTransport(retries=1)
    async with httpx.AsyncClient(transport=transport, timeout=20) as client:
        try:
            response = await client.post(url, json=payload, timeout=1)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            LOGGER.warning("An error occurred while requesting %s.", exc.request.url)
            raise HTTPException(status_code=500, detail=str(exc))
        except httpx.HTTPStatusError as exc:
            status_error_code = exc.response.status_code
            LOGGER.warning(
                "Error response %s while requesting %s.",
                status_error_code,
                exc.request.url,
            )
            raise HTTPException(status_code=status_error_code, detail=exc.response.text)
