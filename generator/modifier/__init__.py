from functools import wraps
import importlib
import pathlib
import generator


_modifiers = {}
_sort = {}
_help = {}


def modifier(name: str, sort: int = 0):

    def decorator(func):

        _modifiers[name] = func
        _sort[name] = sort
        _help[name] = func.__doc__

        @wraps(func)
        def wrapper(sp, songs, *args, **kwargs):
            return func(sp, songs, *args, **kwargs)

        return wrapper

    return decorator


def run_modifiers(sp, songs: list, other_parameters: dict):
    """
    Run modifiers on songs
    :param songs: List of songs to modify
    :param other_parameters: Dictionary containing modifier names as keys
    :return:
    """
    for key, _ in {k: v for k, v in sorted(_sort.items(), key=lambda item: item[1])}.items():
        val = other_parameters.get(key, None)
        if val is None:
            continue
        if generator.verbose:
            generator.logger.info('Running modifier {0}'.format(key))
        mod = _modifiers.get(key)
        if isinstance(val, dict):
            songs = mod(sp, songs, **val)
        else:
            songs = mod(sp, songs, val)
    return songs


def setup():
    """
    Loads in all the modifiers
    :return:
    """
    for file in list(pathlib.Path('generator/modifier').glob('**/*.py')):
        importlib.import_module(str(file).replace('\\', '.').replace('/', '.')[:-3], package=__package__)


def show_all_help():
    for name, detail in _help.items():
        print("""---
        Modifier: {0}
        {1}
        """.format(name.strip(), detail.strip()).replace('\t', '').replace('    ', ''))
