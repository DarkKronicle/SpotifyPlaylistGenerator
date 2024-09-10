from setuptools import find_packages, setup
import pathlib

setup(
    name='SpotifyPlaylistGenerator',
    packages=find_packages(),
    version='0.1.0',
    description='A library for generating Spotify playlists',
    author='DarkKronicle',
    license='MIT',
    scripts=["main.py"],
)
