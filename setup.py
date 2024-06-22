import os
import re

from setuptools import setup


def get_version():
    """get the version from app/__version__.py"""
    version_file = os.path.join(os.path.dirname(__file__), 'app', '__version__.py')
    with open(version_file, 'r') as f:
        version_line = f.read()
        match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_line, re.M)
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string.")


def parse_requirements(filename):
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    return [line for line in lines if line and not line.startswith(('#', '--'))]


setup(
    version=get_version(),
    install_requires=parse_requirements('requirements.txt'),
)
