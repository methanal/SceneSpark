from pydantic import BaseModel


class SubtitleClipperRequest(BaseModel):
    request_id: str
    prompt: str
    model_size: str


class LLMVisionClipperRequest(BaseModel):
    request_id: str
    prompt: str
    sample_interval: float
