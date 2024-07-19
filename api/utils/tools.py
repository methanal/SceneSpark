import base64
import glob
import os
import pickle
import shutil
from pathlib import Path

from app.libs.config import settings


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def purge_dir(_dir: Path):
    for item in _dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def ensure_dir(prefix: Path, request_id: str, purge: bool = False):
    output_dir = prefix / request_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if purge:
        purge_dir(output_dir)

    return output_dir


def load_pickle(request_id: str, pickle_name: str) -> dict:
    pickle_file = Path(f"{settings.CLIPS_BASE_PATH}/{request_id}/{pickle_name}.pkl")
    if pickle_file.exists() and pickle_file.is_file():
        with open(pickle_file, 'rb') as f:
            return pickle.load(f)  # nosec

    return {}


def find_video_files(path: Path) -> list:
    extensions = [
        'mp4',
        'avi',
        'mkv',
        'mov',
        'flv',
        'f4v',
        'wmv',
        'webm',
        'mpeg',
        'mpg',
    ]
    extensions = [ext.lower() for ext in extensions] + [
        ext.upper() for ext in extensions
    ]

    video_files = []
    for ext in extensions:
        video_files.extend(glob.glob(os.path.join(path, f"*.{ext}"), recursive=False))

    return sorted([Path(p) for p in video_files])


def subs_time_to_seconds(time_str: str) -> float:
    """
    Convert a timestamp string(from subtitle) in the format 'H:MM:SS.sss' to seconds.

    Args:
        time_str (str): The timestamp string to convert.

    Returns:
        float: The total time in seconds.

    Example:
        >>> time_str = '0:00:43.290'
        >>> seconds = time_to_seconds(time_str)
        >>> print(seconds)
        43.29
    """
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])

    total_seconds = (hours * 60 * 60) + (minutes * 60) + seconds
    return total_seconds
