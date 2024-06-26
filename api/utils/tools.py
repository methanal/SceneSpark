import base64
import shutil
from pathlib import Path


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def purge_dir(_dir: Path):
    for item in _dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
