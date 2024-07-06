import pickle
from abc import ABC, abstractmethod
from pathlib import Path
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

    def extract_clips(self, prompt: str) -> List[Dict]:
        raise NotImplementedError("BaseClipper.extract_clips not implementted")

    @staticmethod
    def store_clips(videos_segments: List[Dict], clips_path: Path) -> None:
        for item in videos_segments:
            source = item['source']

            media = editor.VideoFileClip(source.as_posix())

            for s in item['segments']:
                start = s['start'] if s['start'] >= 0.0 else 0.0
                end = s['end'] if s['end'] <= media.duration else media.duration
                if start >= media.duration:
                    continue

                clip = media.subclip(start, end)
                aud = clip.audio.set_fps(44100)
                clip: editor.VideoClip = clip.without_audio().set_audio(aud)  # type: ignore[no-redef]
                clip: editor.VideoClip = clip.fx(editor.afx.audio_normalize)  # type: ignore[no-redef]

                _name = clips_path / f"{source.stem}_{start}_{end}.mp4"
                clip.write_videofile(
                    _name.as_posix(), audio_codec="aac", bitrate=settings.BITRATE
                )

                s['file_path'] = settings.VIDEOS_URI_PREFIX / _name.relative_to(
                    settings.CLIPS_BASE_PATH
                )

            media.close()

    @staticmethod
    def pickle_segments_json(obj: List, clips_path: Path) -> None:
        p = clips_path / 'segments.pkl'
        with open(p, 'wb') as f:
            pickle.dump(obj, f)

    @staticmethod
    def flatten_clips_result(videos_segments: List) -> List:
        """
        Inputs:
        [
            {
                'source': '/tmp/videos/source/2.mp4',
                'segments': [
                    {
                        'index': 4,
                        'start': '39.6',
                        'end': '42.05',
                        'subtitle': 'a whisper extract subtitle',
                        'description': 'a llm extract description',
                        'file_path': Path('/tmp/videos/clips/2_39.6.mp4'),
                    },
                    {
                        'index': 6,
                        'start': '49.3',
                        'end': '52',
                        'subtitle': 'a whisper extract subtitle',
                        'description': 'a llm extract description',
                        'file_path': Path('/tmp/videos/clips/2_49.3.mp4'),
                    }
                ]
            },
            {
                'source': '/tmp/videos/source/2.mp4',
                'segments': []
            }
        ]
        """
        flatten_list = []
        for item in videos_segments:
            source = item['source']
            for clip in item['segments']:
                clip['source'] = source
                flatten_list.append(clip)

        return flatten_list
