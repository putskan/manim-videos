from typing import Optional

from manim import *
from pathlib import Path

import numpy as np
import subprocess
import random
import string


def vector_to_latex_format(vector: np.ndarray) -> str:
    """
    Convert a vector to LaTeX format.
    :param vector: 1D numpy array
    :return: str representation of the vector in LaTeX format
    """
    l = [str(elem) for elem in vector]
    return r'\begin{bmatrix}' + r'\\'.join(l) + r'\end{bmatrix}'


def two_dim_span(vector_1: np.ndarray, vector_2: np.ndarray, *args, **kwargs) -> Surface:
    """
    Create a 2D subspace from two vectors (their span).
    :param vector_1: 1D numpy array of length 3
    :param vector_2: 1D numpy array of length 3
    :param args: args to pass to the surface constructor
    :param kwargs: kwargs to pass to the surface constructor
    :return: the 2D subspace
    """
    if len(vector_1) != 3 or len(vector_2) != 3:
        raise ValueError('Vectors must be 3D')

    return Surface(lambda u, v: u * vector_1 + v * vector_2, *args, **kwargs)


def hide_all(scene: Scene) -> None:
    """
    Hide all mobjects in a scene.
    :param scene: the scene to hide
    """
    if scene.mobjects:
        scene.play(
            *[FadeOut(mob) for mob in scene.mobjects]
        )


def text_transition(scene: Scene, text: str) -> None:
    """
    Show a text in a scene.
    :param scene: the scene to show the text in
    :param text: the text to show
    """
    hide_all(scene)
    scene.play(Write(Text(text)))
    scene.wait()
    hide_all(scene)


def _create_random_str(length: int = 7) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _get_video_duration(file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file],
        stdout=subprocess.PIPE,
        text=True
    )
    return float(result.stdout)

def concat_videos(videos_dir: str, video_names: list,
                  keep_existing_audio: bool = False,
                  audio_filepath: Optional[str] = None) -> str:
    """
    combine multiple videos into a single video.
    :param videos_dir: the directory containing the videos
    :param video_names: the names of the videos (extension included)
    :param keep_existing_audio: whether to keep the existing file audios
    :param audio_filepath: audio filepath to add to the output video
    :return: the path to the output video
    """
    videos_dir = Path(videos_dir)
    out_filepath = videos_dir / f'out_{_create_random_str()}.mp4'
    videos_paths = [str(videos_dir / name) for name in video_names]
    videos_paths_formatted = ' '.join(f'-i {path}' for path in videos_paths)

    if keep_existing_audio:
        command = f'ffmpeg {videos_paths_formatted} -filter_complex concat=n={len(video_names)}:v=1:a=1 -c:v libx264 -c:a aac -strict experimental -b:a 192k {out_filepath}'
    else:
        if audio_filepath is not None:
            total_duration = sum(_get_video_duration(file) for file in videos_paths)
            command = f'ffmpeg {videos_paths_formatted} -filter_complex concat=n={len(video_names)}:v=1:a=0 -i {audio_filepath} -c:v libx264 -c:a aac -strict experimental -b:a 192k -t {total_duration} -af "afade=in:st=0:d=3,afade=out:st={total_duration - 3}:d=3" {out_filepath}'
        else:
            command = f'ffmpeg {videos_paths_formatted} -filter_complex concat=n={len(video_names)}:v=1:a=0 -c:v libx264 {out_filepath}'

    subprocess.run(command, shell=True)
    return str(out_filepath)
