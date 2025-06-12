# setup.py
from setuptools import setup, find_packages

setup(
    name="evaluaya",
    version="0.1",
    packages=find_packages(include=["core", "core.*", "utils", "utils.*", "ui", "ui.*"]),
)
