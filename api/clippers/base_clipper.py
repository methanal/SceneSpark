import pickle
from abc import ABC, abstractmethod
from typing import Dict, List

from moviepy import editor

from app.libs.config import settings
from utils.tools import purge_dir


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

    def store_clips(self, segments: List[Dict], purge_path: bool = True) -> None:
        if purge_path:
            purge_dir(self.video_path.parent)

        media = editor.VideoFileClip(self.video_path.as_posix())

        for s in segments:
            start = s['start']
            end = s['end']

            clip = media.subclip(start, end)
            aud = clip.audio.set_fps(44100)
            clip: editor.VideoClip = clip.without_audio().set_audio(aud)  # type: ignore[no-redef]
            clip: editor.VideoClip = clip.fx(editor.afx.audio_normalize)  # type: ignore[no-redef]

            _name = self.video_path.with_name(f"{self.video_path.stem}_{start}.mp4")
            clip.write_videofile(
                _name.as_posix(), audio_codec="aac", bitrate=settings.BITRATE
            )

            s['file_path'] = _name

        media.close()

    def pickle_segments_json(self, obj: List, name: str) -> None:
        with open(f'{name}.pkl', 'wb') as f:
            pickle.dump(obj, f)

    def mark_complete(self) -> None:
        p = self.video_path.parent / 'clip_complete'
        p.touch()
