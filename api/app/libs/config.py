from typing import Dict, Optional, Union

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

    # Frame, after compression, can be successfully sent to the OpenAI API,
    # but may easily reach GPT-4's token limits (30,000 TPM).
    # Consider adjusting the account's TPM, increasing the sample seconds, or switching to a different LLM.
    VIDEO_SAMPLE_INTERVAL_SECOND: float = 4.0  # seconds

    LLM_SUBTITLE_SELECTION_RATIO: str = "三分之一"
    LLM_VIDEO_SELECTION_RATIO: str = "三分之一"

    BITRATE: str = '10m'

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
