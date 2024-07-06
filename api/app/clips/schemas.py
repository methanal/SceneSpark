from pydantic import BaseModel


class SubtitleClipperRequest(BaseModel):
    request_id: str
    prompt: str
    translation_model: str
    model_size: str


class LLMVisionClipperRequest(BaseModel):
    request_id: str
    prompt: str
    sample_interval: float
    clip_duration: float
