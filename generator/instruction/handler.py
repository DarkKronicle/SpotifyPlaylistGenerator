from functools import wraps
import inspect
import generator.spotify as spotify
import typing
import tekore as tk

from generator.context import Context


# All you haters can hate this class, but I find it awesome


class Instruction:
    """
    This is a class to interact with Spotify API and return some sort of Spotify data, typically tracks.

    This is set up so that this can be referenced from within a dictionary containing primitives.
    """

    async def run(self, ctx, **kwargs):
        """
        Run the instruction
        :param ctx: Call context
        :param kwargs: Any other settings that will be used
        :return: Resulting data
        """
        raise NotImplementedError

    def return_type(self):
        """
        The data type that will be returned by 'run'. This is to ensure that the correct instructions are used.
        :return: The type of data that this will return
        """
        raise NotImplementedError


_instructions: dict[str, Instruction] = {}
_help = {}


def _map_parameters(signature: inspect.Signature, *args, **kwargs):
    """
    A utility method that goes through a function's signature and inputted args/kwargs and maps paramater to arg/kwarg.

    Python is a bit annoying with args/kwargs so this makes it easier to deal with it
    :param signature: Signature of the function
    :param args: Input args
    :param kwargs: Input kwargs
    :return: A list of tuples that contains parameter/input
    """
    params = []
    param_vals = list(signature.parameters.values())
    kwargs_copy = dict(kwargs)
    for i in range(len(args)):
        params.append((param_vals[i], args[i]))
    for i in range(len(args), len(param_vals)):
        param = param_vals[i]
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            # Var keyword will always be last so kwargs_copy will be depleted
            # kwargs is not stored as a name in kwargs, just other parameters
            params.append((param, kwargs_copy,))
        elif param.name in kwargs_copy:
            params.append((param, kwargs_copy.pop(param.name),))
        else:
            params.append((param, param.default))
    return params


def _list_of_type(arr, target):
    """
    Checks to see if a list is of the same type
    :param arr: Input list
    :param target: Target type to check
    :return: If the list only contains type target
    """
    return all([isinstance(a, target) for a in arr])


async def _parse_list(ctx: Context, val: list, target):
    """
    Parses a list into the desired list type

    list[str] -> list[tekore.model.Track]
    :param ctx: Call context
    :param val: List of primitives (str/dict)
    :param target: Desired result
    :return: Result
    """
    # type list[<type>]() == list
    if not isinstance(target(), list):
        return val

    if _list_of_type(val, dict):
        # If dict we need instructions
        vals = []
        for d in val:
            vals.extend(await _parse_dict(ctx, d, typing.get_args(target)[0]))
        return vals

    if not _list_of_type(val, str):
        return val

    target_type = typing.get_args(target)[0]
    if target_type == tk.model.Track and ctx.tracks is not None:
        return ctx.tracks
    gotten = [await _parse_other(ctx, q, target_type) for q in val]
    # match typing.get_args(target)[0]:
    #     case tk.model.Track:
    #         gotten = [await ctx.get_track(query) for query in val]
    #     case tk.model.Playlist:
    #         gotten = [await ctx.get_playlist(query) for query in val]
    #     case tk.model.Album:
    #         gotten = [await ctx.get_album(query) for query in val]
    #     case tk.model.Artist:
    #         gotten = [await ctx.get_artist(query) for query in val]
    if gotten is None:
        return val
    return filter(lambda x: x is not None, gotten)


async def _parse_dict(ctx: Context, val: dict, target):
    """
    Parses a dict into the desired target result
    :param ctx: Call context
    :param val: Dictionary
    :param target: Target type (list[tekore.model.Track]...)
    :return: The result that is that type
    """
    kwargs = dict(val)
    name = kwargs.pop('type')
    i = _instructions[name]
    if i.return_type() == target:
        return await run_instruction(name, ctx, **kwargs)
    raise AssertionError('Instruction ' + str(name) + ' with type ' + str(i.return_type()) + ' is not correct for ' + str(target))


async def _parse_other(ctx: Context, val, target):
    """
    Parse a single variable that isn't a dictionary or list
    :param ctx: Call context
    :param val: Value (str)
    :param target: Target type
    :return: Converted result, or just the same
    """
    if isinstance(val, str):
        match target:
            case tk.model.Track:
                return await ctx.get_track(val)
            case tk.model.Album:
                return await ctx.get_album(val)
            case tk.model.Artist:
                return await ctx.get_artist(val)
            case tk.model.Playlist:
                return await ctx.get_playlist(val)
        if target == int:
            return int(val)
        if target == float:
            return float(val)
        if target == bool:
            return bool(val)
    return val


async def parse_var(ctx: Context, target, val):
    """
    Parse a variable of any type
    :param ctx: Call context
    :param target: The target type
    :param val: The parameter's value
    :return: Value converted to parameters target type (if it can find it)
    """
    if isinstance(val, list):
        return await _parse_list(ctx, val, target)
    if isinstance(val, dict):
        if target == Instruction:
            kwargs = val
            instruct = _instructions[kwargs.pop('type')]
            return instruct, kwargs
        return await _parse_dict(ctx, val, target)
    return await _parse_other(ctx, val, target)


async def _parse_func(ctx, signature: inspect.Signature, *args, **kwargs):
    """
    Parse an entire function into Spotify objects. This takes args/kwargs and returns modified ones
    :param ctx: Call context
    :param signature: Function signature
    :param args: Arguments put into function (strings/ints/dicts...)
    :param kwargs: Kwargs put into function (strings/ints/dicts...)
    :return: Modified args/kwargs into the correct data type
    """
    # We are going to make everything kwarg since that is significant easier to modify
    arguments = {}

    # Get list of tuples of parameter to value
    mapped = _map_parameters(signature, *args, **kwargs)
    for param, val in mapped:
        # If it's empty means nothing was provided. (Typically like the spotify client)
        if not isinstance(val, list) and not isinstance(val, dict):
            if val == inspect.Parameter.empty:
                continue
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            # This is kwarg within the kwargs.
            # We just need to map it to the raw value since kwargs can't have target type
            for name, v in val.items():
                arguments[name] = v
        else:
            # Parse the variable into the correct type
            arguments[param.name] = await parse_var(ctx, param.annotation, val)

    # Just return the kwargs
    return (), arguments


def instruction(name: str, *, aliases: typing.Optional[list[str]] = None):
    """
    Generates an instruction that can be called whenever

    The first argument has to be tekore spotify client.
    The function should have *all* of its arguments typed with what it needs, including return. This wrapper
    automatically converts primitives (strings, lists, dictionaries, ints...) into the desired argument (if it can).

    Example:

    If this is the function:

    ```
    def cool_instruction(sp, track: tekore.model.Track, amount: int = 50) -> list[tekore.model.Track]:
        ...
    ```

    a dictionary from the run phase will be passed through, and it's arguments will be converted.

    If track is set to 'MITAMA artist:SANOVA' the track will automatically be searched up. There is a lot of
    flexibility.

    :param name: Name of the instruction. This has to be unique. This will be what the `type` field in a dictionary is
    :param aliases: Aliases that this instruction can be called by
    :return: A wrapper that contains instruction to run
    """

    if aliases is None:
        aliases = []

    aliases = tuple(aliases)

    def decorator(func):

        # We build an instruction object and then modify it's functions
        instruction_obj = Instruction()

        # Signature is important for getting argument types
        signature = inspect.signature(func)

        async def inner_run(ctx, *args, **kwargs):
            # This wraps the function in the ability to be parsed by a dictionary
            args, kwargs = await _parse_func(ctx, signature, *args, **kwargs)
            return await func(ctx, *args, **kwargs)

        def return_type():
            # This is used to check if an instruction is returning the right type for the parameter
            return signature.return_annotation

        instruction_obj.run = inner_run
        instruction_obj.return_type = return_type

        # Add it to the dictionary
        _instructions[name] = instruction_obj
        for a in aliases:
            _instructions[a] = instruction_obj
        _help[(name, aliases)] = func.__doc__

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # If called normally don't do anything, we really just wanted to wrap so we can convert arguments from dict
            return await func(args, kwargs)

        return wrapper

    return decorator


async def run(ctx: Context, val: dict, **kwargs):
    """
    Runs an instruction based off of a dictionary. Dictionary should contain `type` as the name and
    other arguments in key/pair. These are primitives and will automatically be converted when ran.
    :param ctx: Call context
    :param val: Dictionary containing all necessary information to run
    :return: The instruction results
    """
    # We pop this here because we don't want `type` to be an argument
    val = val.copy()
    name = val.pop('type')
    i = _instructions[name]
    return await i.run(ctx, **val, **kwargs)


async def run_instruction(instruction_name, ctx: Context, **kwargs):
    """
    Runs an instruction based off of it's name
    :param instruction_name: Name of the instruction
    :param ctx: Call context
    :param kwargs: All the data that should be passed into run. This should be from TOML (so primitives)
    :return: The result of the ran instruction
    """
    return await _instructions[instruction_name].run(ctx, **kwargs)


def show_all_help():
    for name, detail in _help.items():
        print("""---
        Instruction: {0}
        Aliases: {1}
        {2}
        """.format(name[0].strip(), name[1], detail.strip()).replace('\t', '').replace('    ', ''))
