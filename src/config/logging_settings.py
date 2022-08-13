# flake8: noqa
"""Модуль содержит кастомную настройку для логгера."""

LOG_FORMAT_DEFAULT = '%(levelname)-8s | %(asctime)s | %(name)-30s | %(message)s'
LOG_FORMAT_JSON = '{"level": "%(levelname)s", "time": "%(asctime)s", "logger_name": "%(name)s", "message": "%(message)s"}'
# LOG_FORMAT_JSON = '%(levelname)s | %(asctime)s | %(name)s | %(message)s'
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
            # 'formatter': 'json',
            'handlers': ['file']
        },
        'uvicorn.access': {
            'level': 'INFO',
            # 'formatter': 'json',
            'handlers': ['file']
        },
        'opentelemetry.trace': {
            'level': 'WARNING',
            # 'formatter': 'json',
            'handlers': ['file']
        },
        'security': {
            'level': 'INFO',
            # 'formatter': 'json',
            'handlers': ['file']
        },
    },
    'root': {
        'level': 'INFO',
        # 'formatter': 'default',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}
