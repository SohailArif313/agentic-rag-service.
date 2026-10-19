import logging

import openai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

BILLING_WORDS = ("insufficient_quota", "billing", "exceeded your current quota")


def _short(exc: Exception) -> str:
    return str(exc)[:200]


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(openai.AuthenticationError)
    async def handle_auth(request: Request, exc: openai.AuthenticationError):
        return JSONResponse(
            status_code=401,
            content={"detail": "OpenAI rejected your API key. Please check that it is correct."},
        )

    @app.exception_handler(openai.RateLimitError)
    async def handle_rate_limit(request: Request, exc: openai.RateLimitError):
        logger.warning("OpenAI rate limit or quota error")
        if any(word in str(exc).lower() for word in BILLING_WORDS):
            return JSONResponse(
                status_code=402,
                content={
                    "detail": "There is a billing or quota problem on your OpenAI account. "
                    f"OpenAI says: {_short(exc)}"
                },
            )
        return JSONResponse(
            status_code=429,
            content={"detail": "OpenAI rate limit reached for your key. Wait a little and try again."},
        )

    @app.exception_handler(openai.APIStatusError)
    async def handle_status_error(request: Request, exc: openai.APIStatusError):
        logger.error("OpenAI status error: %s", exc.status_code)
        return JSONResponse(
            status_code=502,
            content={"detail": f"OpenAI returned an error (status {exc.status_code}): {_short(exc)}"},
        )

    @app.exception_handler(openai.OpenAIError)
    async def handle_openai_error(request: Request, exc: openai.OpenAIError):
        logger.error("OpenAI error: %s", type(exc).__name__)
        return JSONResponse(
            status_code=502,
            content={"detail": "Could not get a response from OpenAI. Please try again."},
        )