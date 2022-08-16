# flake8: noqa
"""Модуль содержит кастомную настройку для логгера."""

LOG_FORMAT_DEFAULT = '%(levelname)-8s | %(asctime)s | %(name)-35s | %(message)s'
LOG_FORMAT_JSON = '{"level": "%(levelname)s", "time": "%(asctime)s", "logger_name": "%(name)s", "message": "%(message)s"}'
LOG_DEFAULT_HANDLERS = ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': LOG_FORMAT_JSON
        },
        'default': {
            'format': LOG_FORMAT_DEFAULT,
            'stream': 'ext://sys.stdout'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': 'log.json',
            'maxBytes': 1000000,
            'backupCount': 3,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
    },
    'loggers': {
        'uvicorn.error': {
            'level': 'INFO',
            'handlers': ['file']
        },
        'uvicorn.access': {
            'level': 'WARNING',
            'handlers': ['file']
        },
        'opentelemetry.trace': {
            'level': 'WARNING',
            'handlers': ['file']
        },
        'access': {
            'level': 'INFO',
            'handlers': ['file']
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}
