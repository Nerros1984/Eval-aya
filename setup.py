# setup.py
from setuptools import setup, find_packages

setup(
    name='evaluaya',
    version='0.1.0',
    packages=find_packages(include=['core', 'utils', 'ui']),
    include_package_data=True,
)
