from functools import wraps
import importlib
import pathlib


_modifiers = {}


def modifier(name: str):

    def decorator(func):

        _modifiers[name] = func

        @wraps(func)
        def wrapper(songs, *args, **kwargs):
            return func(songs, *args, **kwargs)

        return wrapper

    return decorator


def run_modifiers(songs: list, other_parameters: dict):
    for key, val in other_parameters.items():
        mod = _modifiers.get(key, None)
        if mod is None:
            print('No modifier named ' + key)
            return songs
        if isinstance(val, dict):
            songs = mod(songs, **val)
        else:
            songs = mod(songs, val)
    return songs


def setup():
    """
    Loads in all the instructions
    :return:
    """
    for file in list(pathlib.Path('generator/modifier').glob('**/*.py')):
        importlib.import_module(str(file).replace('\\', '.').replace('/', '.')[:-3], package=__package__)
