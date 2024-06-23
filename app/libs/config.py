from typing import Any, Dict, Optional, Union

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
    OPENAI_TEMPERATURE: float = 0.4

    def get_llm_provider_config(self, provider: str) -> Dict[str, Union[str, float]]:
        if provider == 'openai':
            return {
                'type': 'remote',
                'model': 'gpt-4o',
                'provider': 'openai',
                'api_key': self.OPENAI_API_KEY,
                'temperature': self.OPENAI_TEMPERATURE,
            }
        else:
            raise ValueError(f"Unsupported provider: {provider}")

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
            'clippers': {
                'handlers': ['stdout'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }


settings = Settings()
