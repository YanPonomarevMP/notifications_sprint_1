"""Модуль содержит функцию конфигурирующую трэйсер."""
from opentelemetry import trace  # type: ignore
from opentelemetry.exporter.jaeger.thrift import JaegerExporter  # type: ignore
from opentelemetry.sdk.resources import Resource  # type: ignore
from opentelemetry.sdk.trace import TracerProvider  # type: ignore
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore

from config.settings import config


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
