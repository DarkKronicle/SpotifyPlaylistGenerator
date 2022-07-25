import generator
from functools import wraps


def modifier(name: str, sort: int = 0):

    def decorator(func):

        _modifiers[name] = func
        _sort[name] = sort
        _help[name] = func.__doc__

        @wraps(func)
        async def wrapper(sp, songs, *args, **kwargs):
            return await func(sp, songs, *args, **kwargs)

        return wrapper

    return decorator


_modifiers = {}
_sort = {}
_help = {}


async def run_modifiers(sp, songs: list, other_parameters: dict):
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
            songs = await mod(sp, songs, **val)
        else:
            songs = await mod(sp, songs, val)
    return songs


def show_all_help():
    for name, detail in _help.items():
        print("""---
        Modifier: {0}
        {1}
        """.format(name.strip(), detail.strip()).replace('\t', '').replace('    ', ''))
