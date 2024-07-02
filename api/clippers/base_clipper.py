import pickle
from abc import ABC, abstractmethod
from typing import Dict, List

from moviepy import editor

from app.libs.config import settings


class IClipper(ABC):
    """
    IClipper serves as an interface for clipping video segments.
    Classes that implement this interface should define the method to extract clips from a given video.
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def extract_clips(self, prompt: str) -> List[Dict]:
        """
        Extract clips from the video and return a list of JSON objects.

        Each JSON object contains the start and end time of the video segment,
        as well as a detailed description including tags and a brief description
        for each clip.

        Returns:
        --------
        List[Dict]
            A list of dictionaries with start and end times and JSON descriptions.
        """
        raise NotImplementedError(
            "IClipper.extract_clips must be overridden by subclasses"
        )


class BaseClipper(IClipper):
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def video_path(self):
        pass

    def extract_clips(self, prompt: str) -> List[Dict]:
        raise NotImplementedError("BaseClipper.extract_clips not implementted")

    def store_clips(self, segments: List[Dict]) -> None:
        media = editor.VideoFileClip(self.video_path.as_posix())

        for s in segments:
            start = s['start'] if s['start'] >= 0.0 else 0.0
            end = s['end'] if s['end'] <= media.duration else media.duration

            clip = media.subclip(start, end)
            aud = clip.audio.set_fps(44100)
            clip: editor.VideoClip = clip.without_audio().set_audio(aud)  # type: ignore[no-redef]
            clip: editor.VideoClip = clip.fx(editor.afx.audio_normalize)  # type: ignore[no-redef]

            _name = self.video_path.with_name(
                f"{self.video_path.stem}_{start}_{end}.mp4"
            )
            clip.write_videofile(
                _name.as_posix(), audio_codec="aac", bitrate=settings.BITRATE
            )

            s['file_path'] = settings.VIDEOS_URI_PREFIX / _name.relative_to(
                settings.UPLOAD_BASE_PATH
            )

        media.close()

    def pickle_segments_json(self, obj: List, name: str) -> None:
        p = self.video_path.parent / f'{name}.pkl'
        with open(p, 'wb') as f:
            pickle.dump(obj, f)

    def mark_complete(self, suffix: str = '') -> None:
        p = self.video_path.parent / f'clip_complete.{suffix}'
        p.touch()
