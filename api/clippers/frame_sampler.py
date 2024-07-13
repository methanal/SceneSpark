from enum import Enum, auto
from pathlib import Path
from typing import Optional, Union

import cv2
import srt


class FrameSampler(Enum):
    TIME_BASE = auto()
    SUBTITLE_BASE = auto()


def time_framer(
    video_file: Path,
    sample_interval: float,
    clip_duration: float,
    save_image: bool = True,
) -> tuple[list[Optional[bytes]], list[dict[str, Union[float, str]]]]:
    video = cv2.VideoCapture(video_file)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)
    total_duration = total_frame / fps

    interval_frames = int(fps * sample_interval)
    frame_count = 0
    encoded_frames = []

    offset = clip_duration / 2
    time_frames = []

    while True:
        ret, frame = video.read()
        # _png_path = video_file.parent / f'{frame_count}.png'
        # cv2.imwrite(_png_path, frame)
        if not ret:
            break

        if frame_count % interval_frames == 0:
            ret, _buffer = cv2.imencode(
                '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 45]
            )
            if not ret:
                continue

            encoded_frames.append(_buffer.tobytes())

            time_point = frame_count / fps
            start = time_point - offset
            end = time_point + offset
            time_frames.append(
                {
                    'time_point': time_point,
                    'start': start if start >= 0.0 else 0.0,
                    'end': end if end <= total_duration else total_duration,
                }
            )

            if save_image:
                _img_path = video_file.parent / f'{time_point}.jpg'
                with open(_img_path, "wb") as f:
                    f.write(_buffer.tobytes())

        frame_count += 1

    video.release()

    return encoded_frames, time_frames


def subtitle_framer(
    video_file: Path,
    sample_interval: float,
    clip_duration: float,
    subtitles: list,
    save_image: bool = True,
) -> tuple[list[Optional[bytes]], list[dict[str, Union[float, str]]]]:
    time_frames = get_time_frames(sample_interval, clip_duration, subtitles)

    video = cv2.VideoCapture(video_file)
    fps = video.get(cv2.CAP_PROP_FPS)

    encoded_frames: list[Optional[bytes]] = []
    for tf in time_frames:
        time_point = tf['time_point']
        frame_idx = int(round(time_point * fps))
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = video.read()
        if not ret:
            encoded_frames.append(None)
            continue

        ret, _buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 45])
        if not ret:
            encoded_frames.append(None)
            continue

        encoded_frames.append(_buffer.tobytes())

        if save_image:
            _img_path = video_file.parent / f'{time_point}.jpg'
            with open(_img_path, "wb") as f:
                f.write(_buffer.tobytes())

    return encoded_frames, time_frames


def get_time_frames(
    sample_interval: float,
    clip_duration: float,
    subtitles: list,
) -> list[dict[str, Union[float, str]]]:
    time_frames = []
    offset = clip_duration / 2

    for idx, sub in enumerate(subtitles[:-1]):
        _srt = srt.compose([sub])
        start = sub.start.total_seconds()
        end = sub.end.total_seconds()

        if sub.content != '< No Speech >':
            # first frame of subtitle section
            time_frames.append(
                {
                    'time_point': start,
                    'start': start,
                    'end': end,
                    'srt': _srt,
                }
            )

            # every sample_interval of subtitle section
            shift = start
            while (time_point := shift + sample_interval) < end:
                time_frames.append(
                    {
                        'time_point': time_point,
                        'start': start,
                        'end': end,
                        'srt': _srt,
                    }
                )
                shift = time_point

            silence_start = end
        else:
            silence_start = start

        # every sample_interval of silence (none subtitle) section
        next_sub = subtitles[idx + 1]
        next_sub_start = next_sub.start.total_seconds()
        while (time_point := silence_start + sample_interval) < next_sub_start:
            time_frames.append(
                {
                    'time_point': time_point,
                    'start': time_point - offset,
                    'end': time_point + offset,
                    'srt': _srt,
                }
            )
            silence_start = time_point

    return time_frames
