import inspect
import logging
import traceback
from pprint import pprint
from typing import Optional

import generator
from functools import wraps

from generator.context import Context
from generator.instruction.handler import _parse_func


def modifier(name: str, sort: int = 0, *, aliases: Optional[list] = None):

    if aliases is None:
        aliases = []

    aliases = tuple(aliases)

    def decorator(func):

        signature = inspect.signature(func)

        async def inner_run(ctx, songs, *args, **kwargs):
            # This wraps the function in the ability to be parsed by a dictionary
            args = (ctx, songs) + args
            args, kwargs = await _parse_func(ctx, signature, *args, **kwargs)
            return await func(*args, **kwargs)

        _modifiers[name] = inner_run
        for a in aliases:
            _modifiers[a] = inner_run
        _sort[name] = sort
        _help[(name, aliases)] = func.__doc__

        @wraps(func)
        async def wrapper(ctx, songs, *args, **kwargs):
            return await func(ctx, songs, *args, **kwargs)

        return wrapper

    return decorator


_modifiers = {}
_sort = {}
_help = {}


async def run_modifiers(ctx: Context, songs: list, other_parameters: dict):
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
        try:
            if isinstance(val, dict):
                songs = await mod(ctx, songs, **val)
            else:
                songs = await mod(ctx, songs, val)
        except:
            logging.warning('Could not run modifier {0}'.format(key))
            traceback.print_exc()
    return songs


def show_all_help():
    for name, detail in _help.items():
        print("""---
        Modifier: {0}
        Aliases: {1}
        {2}
        """.format(name[0].strip(), name[1], detail.strip()).replace('\t', '').replace('    ', ''))
