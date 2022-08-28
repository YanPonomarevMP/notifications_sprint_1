"""Модуль содержит конфигурацию приложения FastAPI."""

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.v1.emails.main import router as v1_emails_router
from config.logging_settings import LOGGING
from config.settings import config
from utils.custom_exceptions_handlers import validation_exception_handler, http_exception_handler
from utils.dependencies import authorization_required
from utils.startup_shutdown import startup, shutdown
from utils.tracer import configure_tracer

app = FastAPI(
    title=config.fast_api.swagger_docs.title,
    description=config.fast_api.swagger_docs.description,
    version=config.fast_api.swagger_docs.version,
    docs_url=config.fast_api.swagger_docs.docs_url,
    openapi_url=config.fast_api.swagger_docs.openapi_url,
    default_response_class=ORJSONResponse,
    on_startup=[
        startup
    ],
    on_shutdown=[
        shutdown
    ],
    exception_handlers={
        RequestValidationError: validation_exception_handler,
        StarletteHTTPException: http_exception_handler
    },
    dependencies=[
        Depends(authorization_required),
    ]
)

configure_tracer()
FastAPIInstrumentor().instrument_app(app)

app.include_router(v1_emails_router, prefix='/v1')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.fast_api.host,
        port=config.fast_api.port,
        log_config=LOGGING,
    )
