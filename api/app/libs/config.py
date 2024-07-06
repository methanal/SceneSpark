from pathlib import Path
from typing import Dict, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    # Frame, after compression, can be successfully sent to the OpenAI API,
    # but may easily reach GPT-4's token limits (30,000 TPM).
    # Consider adjusting the account's TPM, increasing the sample seconds, or switching to a different LLM.
    VIDEO_SAMPLE_INTERVAL_SECOND: float = 4.0  # seconds

    VIDEOS_BASE_PATH: str = ''

    VIDEOS_URI_PREFIX: Path = Path('/videos/clips')

    LLM_SUBTITLE_SELECTION_RATIO: str = "三分之一"
    LLM_VIDEO_SELECTION_RATIO: str = "三分之一"

    SENTRY_DSN: str = ''
    SENTRY_APM_SAMPLE_RATE: Optional[float] = 1

    BITRATE: str = '10m'

    OPENAI_API_KEY: str = ''
    OPENAI_BASE_URL: str = ''
    OPENAI_TEMPERATURE: float = 0.4

    @field_validator('VIDEOS_BASE_PATH')
    def validate_path(cls, v):
        path = Path(v)
        if not path.exists():
            raise ValueError(f'Path {v} does not exist')
        return path

    @property
    def UPLOAD_BASE_PATH(self) -> Path:
        return Path(self.VIDEOS_BASE_PATH) / 'source'

    @property
    def CLIPS_BASE_PATH(self) -> Path:
        return Path(self.VIDEOS_BASE_PATH) / 'clips'

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


settings = Settings()
