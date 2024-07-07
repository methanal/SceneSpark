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
    def extract_clips(self, prompt: str) -> Dict:
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

    def extract_clips(self, prompt: str) -> Dict:
        raise NotImplementedError("BaseClipper.extract_clips not implementted")

    @staticmethod
    def store_clips(videos_segments: Dict[Path, list], clips_path: Path) -> None:
        for source, segments in videos_segments.items():

            media = editor.VideoFileClip(source.as_posix())

            for s in segments:
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
    def pickle_segments_json(obj: Dict, clips_path: Path, name: str) -> None:
        p = clips_path / f'{name}.pkl'
        with open(p, 'wb') as f:
            pickle.dump(obj, f)

    @staticmethod
    def flatten_clips_result(videos_segments: Dict) -> List:
        """
        Inputs:
        {
            '/tmp/videos/source/2.mp4': [
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
            ],
            '/tmp/videos/source/4.mp4': []
        }
        """
        flatten_list = []
        for source, segments in videos_segments.items():
            for clip in segments:
                clip['source'] = source
                flatten_list.append(clip)

        return flatten_list

    @staticmethod
    def merge_clips_dict(dict1, dict2) -> Dict:
        def _is_overlapping(start1, end1, start2, end2):
            return max(start1, start2) < min(end1, end2)

        def _merge_segments(segment_list1, segment_list2):
            merged_segments = segment_list1.copy()

            for seg2 in segment_list2:
                for seg1 in merged_segments:
                    if _is_overlapping(
                        seg1['start'], seg1['end'], seg2['start'], seg2['end']
                    ):
                        seg1['start'] = min(seg1['start'], seg2['start'])
                        seg1['end'] = max(seg1['end'], seg2['end'])
                        seg1['tags'] = list(
                            set(seg1.get('tags', []) + seg2.get('tags', []))
                        )

                        for key in seg2:
                            if key not in ['start', 'end', 'tags']:
                                seg1[key] = (
                                    [seg1[key], seg2[key]] if key in seg1 else seg2[key]
                                )

                        break
                else:
                    merged_segments.append(seg2)

            merged_segments.sort(key=lambda x: x['start'])
            return merged_segments

        merged_dict = {}

        all_keys = set(dict1.keys()).union(set(dict2.keys()))

        for key in all_keys:
            segments1 = dict1.get(key, [])
            segments2 = dict2.get(key, [])
            merged_segments = _merge_segments(segments1, segments2)
            merged_dict[key] = merged_segments

        return merged_dict
