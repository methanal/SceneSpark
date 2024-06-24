import shutil
from pathlib import Path


def purge_dir(_dir: Path):
    for item in _dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
