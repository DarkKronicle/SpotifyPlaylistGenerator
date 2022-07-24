from setuptools import find_packages, setup
import pathlib

requirements = [s.strip() for s in pathlib.Path('requirements.txt').read_text().split('\n')]

setup(
    name='spotifygenerator',
    packages=find_packages(include=['generator']),
    version='0.1.0',
    description='A library for generating Spotify playlists',
    author='DarkKronicle',
    license='MIT',
    install_requires=requirements,
)
