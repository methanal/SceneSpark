import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional

import orjson
import srt
from autocut.transcribe import Transcribe
from autocut.utils import is_video, load_audio
from moviepy import editor

from clippers.base_clipper import BaseClipper
from clippers.wrappers.openai_wrapper import pick_srts, srts_client

LOGGER = logging.getLogger(__name__)


class SubtitleClipper(BaseClipper):
    def __init__(self, autocut_args):
        super().__init__()
        self.autocut_args = autocut_args

    def extract_clips(self, video_path: Path, prompt: str) -> List[Dict]:
        self.autocut_args.inputs = [video_path]

        subs, srts = self.__transcribe_srt(video_path)

        _srts_json = pick_srts(srts_client, srts, prompt)
        subs_info = orjson.loads(_srts_json)

        selected_subs = [subs[int(s["index"]) - 1] for s in subs_info]
        clip_metadata_list = self._store_clips(video_path, selected_subs)

        for metadata, s in zip(clip_metadata_list, subs_info):
            metadata['extract'] = s['extract']

        return clip_metadata_list

    def _store_clips(self, video_path: Path, subs) -> List[Dict]:
        segments: List[Dict] = []

        subs.sort(key=lambda x: x.start)
        for x in subs:
            if len(segments) == 0:
                segments.append(
                    {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                )
            else:
                if x.start.total_seconds() - segments[-1]["end"] < 0.5:
                    segments[-1]["end"] = x.end.total_seconds()
                else:
                    segments.append(
                        {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                    )

        media = editor.VideoFileClip(video_path.as_posix())

        clip_metadata_list = []
        for s in segments:
            start = s['start']
            end = s['end']

            clip = media.subclip(start, end)
            aud = clip.audio.set_fps(44100)
            clip: editor.VideoClip = clip.without_audio().set_audio(aud)  # type: ignore[no-redef]
            clip: editor.VideoClip = clip.fx(editor.afx.audio_normalize)  # type: ignore[no-redef]

            _name = video_path.with_name(f"{video_path.stem}_{start}.mp4")
            clip.write_videofile(
                _name.as_posix(), audio_codec="aac", bitrate=self.autocut_args.bitrate
            )

            clip_metadata_list.append(
                {"start_time": start, "end_time": end, "file_path": _name.as_posix()}
            )

        media.close()

        logging.debug(f"cut media to {clip_metadata_list}")  # noqa: G004
        return clip_metadata_list

    def __transcribe_srt(self, video_path: Path):
        if not is_video(video_path):
            LOGGER.warning(f"{video_path} isn't a valid video.")  # noqa: G004

        transcriber = Transcribe(self.autocut_args)

        audio = load_audio(video_path, sr=transcriber.sampling_rate)
        speech_array_indices = transcriber._detect_voice_activity(audio)
        transcribe_results = transcriber._transcribe(
            video_path, audio, speech_array_indices
        )

        subs = transcriber.whisper_model.gen_srt(transcribe_results)
        srts = srt.compose(subs)
        LOGGER.debug(f"{srts}")  # noqa: G004
        return subs, srts

    @staticmethod
    def gen_args(
        inputs: Optional[list] = None,
        prompt: str = '',
        whisper_mode: str = 'whisper',
        whisper_model: str = 'small',
        device: Optional[str] = None,
    ):
        return argparse.Namespace(
            inputs=inputs,
            transcribe=None,
            cut=None,
            daemon=True,
            s=None,
            to_md=None,
            lang='zh',
            prompt=prompt,
            whisper_mode=whisper_mode,
            openai_rpm=3,
            whisper_model=whisper_model,
            bitrate='10m',
            vad='auto',
            force=None,
            encoding='utf-8',
            device=None,
        )

    @staticmethod
    def all_cut_ready(path: Path):
        """检查目录下，每个 {name}.{suffix}，都有对应的 {name}_cut.mp4 文件"""
        ret_files = []
        for file in path.iterdir():
            if is_video(file) and '_cut' not in file.stem:
                cut_file = file.with_name(f"{file.stem}_cut.mp4")
                if not cut_file.exists():
                    return []

                ret_files.append(cut_file)

        return ret_files

    @staticmethod
    def merge_videos(
        cut_files: List[Path], session_path: Path, merge_filename: Path, bitrate='10m'
    ):
        videos = []
        for file in cut_files:
            videos.append(editor.VideoFileClip(file.as_posix()))

        dur = sum([v.duration for v in videos])
        logging.info(
            f"Merging into a video with {dur / 60:.1f} min length"  # noqa: G004
        )

        merged = editor.concatenate_videoclips(videos)

        merged.write_videofile(
            merge_filename.as_posix(), audio_codec="aac", bitrate=bitrate
        )

        logging.info(f"Saved merged video to {merge_filename}")  # noqa: G004
