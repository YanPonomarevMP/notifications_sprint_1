"""Модуль содержит конфигурацию приложения FastAPI."""

import aiohttp
# import sentry_sdk
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from opentelemetry import trace  # type: ignore
from opentelemetry.exporter.jaeger.thrift import JaegerExporter  # type: ignore
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
from opentelemetry.sdk.resources import Resource  # type: ignore
from opentelemetry.sdk.trace import TracerProvider  # type: ignore
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore

from api.v1.emails.main import router as v1_emails_router
# from api_config.fast_api_logging import LOGGING
from config.app_settings import config
from config.logging_settings import LOGGING
from db.storage import orm_factory
from utils import aiohttp_session
from utils.dependencies import x_request_id_required

# from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
# from api_config.fast_api_logging import LOGGING
# from models.request_log import RequestLog

app = FastAPI(
    title=config.fast_api.swagger_docs.title,
    description=config.fast_api.swagger_docs.description,
    version=config.fast_api.swagger_docs.version,
    docs_url=config.fast_api.swagger_docs.docs_url,
    openapi_url=config.fast_api.swagger_docs.openapi_url,
    default_response_class=ORJSONResponse,
    dependencies=[Depends(x_request_id_required)]
)


# sentry_sdk.init(
#     dsn=api_config.logging.sentry_dsn,
#     environment=api_config.logging.sentry_env
# )
#
# try:
#     app.add_middleware(SentryAsgiMiddleware)
# except Exception:  # noqa: S110
#     pass


def configure_tracer() -> None:

    """Функция конфигурирует трэйсер."""

    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create(
                {
                    'service.name': 'UGC',
                }
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=config.jaeger.host,
                agent_port=config.jaeger.port,
            )
        )
    )


# logger = create_logger(__name__)


@app.on_event('startup')
async def startup() -> None:

    """Функция, для действий во время старта приложения."""

    # async_backoff.logger = await async_log.create_logger('Backoff')

    headers = {'Authorization': config.auth_api.access_token.get_secret_value()}
    aiohttp_session.session = aiohttp.ClientSession(headers=headers)
    #
    # await event_broker.start()
    await orm_factory.db.start()


@app.on_event('shutdown')
async def shutdown() -> None:

    """Функция, для действий во время завершения работы приложения."""

    await aiohttp_session.session.close()  # type: ignore
    # await event_broker.stop()
    await orm_factory.db.stop()


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
