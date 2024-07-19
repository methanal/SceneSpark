from pydantic import BaseModel


class SubtitleClipperRequest(BaseModel):
    request_id: str
    prompt: str
    translation_model: str
    model_size: str
    whisper_prompt: str


class LLMVisionClipperRequest(BaseModel):
    request_id: str
    prompt: str
    sample_interval: float
    clip_duration: float


class MergeJsonRequest(BaseModel):
    request_id: str


class VisionWithSrtClipperRequest(BaseModel):
    request_id: str
    translation_model: str
    model_size: str
    sample_interval: float
    clip_duration: float
    whisper_prompt: str
    prompt: str


class VideoMetaClipperRequest(BaseModel):
    request_id: str
    translation_model: str
    model_size: str
    sample_interval: float
    clip_duration: float
    prompt_frame_desc_subs: str
    prompt_frame_tag_score: str
    prompt_video_meta: str
