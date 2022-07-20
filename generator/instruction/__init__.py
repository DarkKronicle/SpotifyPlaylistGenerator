from functools import wraps
import inspect
import tekore as tk
import generator.spotify as spotify
import typing
import pathlib
import importlib


# All you haters can hate this class, but I find it awesome


class Instruction:
    """
    This is a class to interact with Spotify API and return some sort of Spotify data, typically tracks.

    This is set up so that this can be referenced from within a dictionary containing primitives.
    """

    def run(self, sp, **kwargs):
        """
        Run the instruction
        :param sp: Tekore Spotify client
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
    for i in range(len(args)):
        params.append((param_vals[i], args[i]))
    for i in range(len(args), len(param_vals)):
        param = param_vals[i]
        if param.name in kwargs:
            params.append((param, kwargs[param.name]))
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


def _parse_list(sp, val: list, target):
    """
    Parses a list into the desired list type

    list[str] -> list[tekore.model.Track]
    :param sp: Tekore Spotify client
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
            vals.extend(_parse_dict(sp, d, typing.get_args(target)[0]))
        return vals

    if not _list_of_type(val, str):
        return val

    match typing.get_args(target)[0]:
        case tk.model.Track:
            return [spotify.get_track(sp, query) for query in val]
        case tk.model.Playlist:
            return [spotify.get_playlist(sp, query) for query in val]
        case tk.model.Album:
            return [spotify.get_album(sp, query) for query in val]
        case tk.model.Artist:
            return [spotify.get_artist(sp, query) for query in val]
    return val


def _parse_dict(sp, val: dict, target):
    """
    Parses a dict into the desired target result
    :param sp: Tekore Spotify client
    :param val: Dictionary
    :param target: Target type (list[tekore.model.Track]...)
    :return: The result that is that type
    """
    kwargs = dict(val)
    name = kwargs.pop('type')
    i = _instructions[name]
    if i.return_type() == target:
        return run_instruction(name, sp, **kwargs)
    raise AssertionError('Instruction ' + str(name) + ' with type ' + str(i.return_type()) + ' is not correct for ' + str(target))


def _parse_other(sp, val, target):
    """
    Parse a single variable that isn't a dictionary or list
    :param sp: Tekore Spotify client
    :param val: Value (str)
    :param target: Target type
    :return: Converted result, or just the same
    """
    if isinstance(val, str):
        match target:
            case tk.model.Track:
                return spotify.get_track(sp, val)
            case tk.model.Album:
                return spotify.get_album(sp, val)
            case tk.model.Artist:
                return spotify.get_artist(sp, val)
            case tk.model.Playlist:
                return spotify.get_playlist(sp, val)
    return val


def _parse_var(sp, target, val):
    """
    Parse a variable of any type
    :param sp: Tekore Spotify client
    :param target: The target type
    :param val: The parameter's value
    :return: Value converted to parameters target type (if it can find it)
    """
    if isinstance(val, list):
        return _parse_list(sp, val, target)
    if isinstance(val, dict):
        if target == Instruction:
            kwargs = val['type']
            instruct = _instructions[kwargs.pop('type')]
            return instruct, kwargs
        return _parse_dict(sp, val, target)
    return _parse_other(sp, val, target)


def _parse_func(sp, signature: inspect.Signature, *args, **kwargs):
    """
    Parse an entire function into Spotify objects. This takes args/kwargs and returns modified ones
    :param sp: Tekore Spotify client
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
        if val == inspect.Parameter.empty:
            continue
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            # This is kwarg within the kwargs.
            # We just need to map it to the raw value since kwargs can't have target type
            for name, v in val.items():
                arguments[name] = v
        else:
            # Parse the variable into the correct type
            arguments[param.name] = _parse_var(sp, param.annotation, val)

    # Just return the kwargs
    return (), arguments


def instruction(name: str):
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
    :return: A wrapper that contains instruction to run
    """

    def decorator(func):

        # We build an instruction object and then modify it's functions
        instruction_obj = Instruction()

        # Signature is important for getting argument types
        signature = inspect.signature(func)

        def inner_run(sp, *args, **kwargs):
            # This wraps the function in the ability to be parsed by a dictionary
            args, kwargs = _parse_func(sp, signature, *args, **kwargs)
            return func(sp, *args, **kwargs)

        def return_type():
            # This is used to check if an instruction is returning the right type for the parameter
            return signature.return_annotation

        instruction_obj.run = inner_run
        instruction_obj.return_type = return_type

        # Add it to the dictionary
        _instructions[name] = instruction_obj
        _help[name] = func.__doc__

        @wraps(func)
        def wrapper(*args, **kwargs):
            # If called normally don't do anything, we really just wanted to wrap so we can convert arguments from dict
            return func(args, kwargs)

        return wrapper

    return decorator


def run(sp, val: dict):
    """
    Runs an instruction based off of a dictionary. Dictionary should contain `type` as the name and
    other arguments in key/pair. These are primitives and will automatically be converted when ran.
    :param sp: Tekore Spotify client
    :param val: Dictionary containing all necessary information to run
    :return: The instruction results
    """
    # We pop this here because we don't want `type` to be an argument
    name = val.pop('type')
    i = _instructions[name]
    return i.run(sp, **val)


def run_instruction(name, sp, **kwargs):
    """
    Runs an instruction based off of it's name
    :param name: Name of the instruction
    :param sp: Tekore Spotify client
    :param kwargs: All the data that should be passed into run. This should be from TOML (so primitives)
    :return: The result of the ran instruction
    """
    return _instructions[name].run(sp, **kwargs)


def setup():
    """
    Loads in all the instructions
    :return:
    """
    for file in list(pathlib.Path('generator/instruction').glob('**/*.py')):
        importlib.import_module(str(file).replace('\\', '.').replace('/', '.')[:-3], package=__package__)


def show_all_help():
    for name, detail in _help.items():
        print("""---
        Instruction: {0}
        {1}
        """.format(name.strip(), detail.strip()).replace('\t', '').replace('    ', ''))
