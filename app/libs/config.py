from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    DEBUG: bool = False

    SENTRY_DSN: str = ''
    SENTRY_APM_SAMPLE_RATE: Optional[float] = 1
    OPENAI_API_KEY: str = ''
    OPENAI_BASE_URL: str = ''

    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                '()': 'logging.Formatter',
                'fmt': '[{levelname:1.1s} {asctime} {module}:{funcName}:{lineno}] {message}',  # noqa: E501
                'style': '{',
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default',
            },
        },
        'loggers': {
            'SceneSpark': {
                'handlers': ['stdout'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'app': {
                'handlers': ['stdout'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'utils': {
                'handlers': ['stdout'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }


settings = Settings()
