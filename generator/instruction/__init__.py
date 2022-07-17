from functools import wraps
import inspect
import tekore as tk
import generator.spotify as spotify


# All you haters can hate this class, but I find it awesome


class Instruction:

    def run(self, sp, **kwargs):
        raise NotImplementedError

    def return_type(self):
        raise NotImplementedError


_instructions: dict[str, Instruction] = {}


def run_instruction(name, sp, **kwargs):
    _instructions[name].run(sp, **kwargs)


def _map_parameters(signature: inspect.Signature, *args, **kwargs):
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
    return all([isinstance(a, target) for a in arr])


def _parse_list(sp, val: list, target):
    if target == list[tk.model.Track]:
        if _list_of_type(val, str):
            return [spotify.get_track(sp, query) for query in val]
        vals = []
        for d in val:
            vals.extend(_parse_dict(sp, d, target[0]))
        return vals
    if target == list[tk.model.Playlist]:
        if _list_of_type(val, str):
            return [spotify.get_playlist(sp, query) for query in val]
        vals = []
        for d in val:
            vals.extend(_parse_dict(sp, d, target[0]))
        return vals
    if target == list[tk.model.Album]:
        if _list_of_type(val, str):
            return [spotify.get_album(sp, query) for query in val]
        vals = []
        for d in val:
            vals.extend(_parse_dict(sp, d, target[0]))
        return vals
    if target == list[tk.model.Artist]:
        if _list_of_type(val, str):
            return [spotify.get_artist(sp, query) for query in val]
        vals = []
        for d in val:
            vals.extend(_parse_dict(sp, d, target[0]))
        return vals
    return val


def _parse_dict(sp, val: dict, target):
    kwargs = dict(val)
    name = kwargs.pop('type')
    i = _instructions[name]
    # TODO this doesn't work so...
    if i.return_type() == target:
        return run_instruction(name, sp, **kwargs)
    raise AssertionError('Instruction ' + str(name) + ' with type ' + str(i.return_type()) + ' is not correct for ' + str(target))


def _parse_other(sp, val, target):
    if isinstance(val, str):
        if target == tk.model.Track:
            return spotify.get_track(sp, val)
        if target == tk.model.Album:
            return spotify.get_album(sp, val)
        if target == tk.model.Artist:
            return spotify.get_artist(sp, val)
        if target == tk.model.Playlist:
            return spotify.get_playlist(sp, val)
        return val
    return val


def _parse_var(sp, param, val):
    if isinstance(val, list):
        return _parse_list(sp, val, param.annotation)
    if isinstance(val, dict):
        if param.annotation == Instruction:
            kwargs = val['type']
            instruct = _instructions[kwargs.pop('type')]
            return instruct, kwargs
        return _parse_dict(sp, val, param.annotation)
    return _parse_other(sp, val, param.annotation)


def _parse_func(sp, signature: inspect.Signature, *args, **kwargs):
    # We are gonna make everything KWARG!!!
    arguments = {}
    mapped = _map_parameters(signature, *args, **kwargs)
    for param, val in mapped:
        if val == inspect.Parameter.empty:
            continue
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            for name, v in val.items():
                arguments[name] = v
        else:
            arguments[param.name] = _parse_var(sp, param, val)

    return (), arguments


def run(sp, val: dict):
    name = val.pop('type')
    i = _instructions[name]
    return i.run(sp, **val)


def instruction(name: str):

    def decorator(func):

        instruction_obj = Instruction()

        signature = inspect.signature(func)

        def inner_run(sp, *args, **kwargs):
            args, kwargs = _parse_func(sp, signature, *args, **kwargs)
            return func(sp, *args, **kwargs)

        def return_type():
            return signature.return_annotation

        instruction_obj.run = inner_run
        instruction_obj.return_type = return_type

        _instructions[name] = instruction_obj

        @wraps(func)
        def wrapper(*args, **kwargs):
            # If called normally don't do anything, we really just wanted to wrap so we can use strings and such
            return func(args, kwargs)

        return wrapper

    return decorator

