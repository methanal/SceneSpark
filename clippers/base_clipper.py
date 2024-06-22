from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List


class IClipper(ABC):
    """
    IClipper serves as an interface for clipping video segments.
    Classes that implement this interface should define the method to extract clips from a given video.
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def extract_clips(self, video_path: Path, prompt: str) -> List[Dict]:
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
    def __init__(self, autocut_args):
        super().__init__()

    def extract_clips(self, video_path: Path, prompt: str) -> List[Dict]:
        raise NotImplementedError("BaseClipper.extract_clips not implementted")
