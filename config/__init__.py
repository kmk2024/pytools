# -*- coding: utf-8 -*-
import inspect
import os.path
import sys
import turtle
from functools import wraps
from importlib import resources

import win32api
import win32con
import win32gui

from config.config import Config

_config: Config = None
required_input_tag = '_required_type'


def init(_config: Config) -> None:
    hwnd = win32gui.GetForegroundWindow()
    en = 0x0409
    win32api.SendMessage(
        hwnd,
        win32con.WM_INPUTLANGCHANGEREQUEST,
        0,
        en
    )


def get_config() -> Config:
    global _config
    if not _config:
        try:
            config_file = (resources.files('resources') / 'config/config.yaml')
        except:
            application_path = os.path.dirname(sys.executable)
            config_file = f"{application_path}/config/config.yaml"
        _config = Config(config_file)
        init(_config)
        return _config


def config(*args, **kwargs):
    def inner(obj):
        config_tag = obj.__name__
        if inspect.isfunction(obj):
            func_args = {}
            method_args = inspect.getfullargspec(obj).args
            for arg in args:
                if arg not in method_args:
                    method_args.append(arg)
            _required = kwargs.get(required_input_tag)
            for name in method_args:
                if _required:
                    func_args[name] = get_config().get_create_config(f"{config_tag}.{name}", None, _required)
                else:
                    func_args[name] = get_config().get_config(f"{config_tag}.{name}")
            if not _required:
                for name in kwargs.keys():
                    func_args[name] = get_config().get_create_config(f"{config_tag}.{name}", kwargs.get(name))
            @wraps(obj)
            def function_inner(*args, **kwargs):
                assert len(args) == 0, f"config doesnt support args {args}"
                for key in func_args.keys():
                    _value = kwargs.get(key)
                    if not _value:
                        kwargs[key] = func_args[key]
                result = obj(*arg, **kwargs)
                return result
            return function_inner
        else:
            _required = kwargs.get(required_input_tag)
            for name in args:
                if _required:
                    setattr(obj, name, get_config().get_create_config(f"{config_tag}.{name}", None, _required))
                else:
                    setattr(obj, name, get_config().get_create_config(f"{config_tag}.{name}"))
            if not _required:
                for name in kwargs.keys():
                    setattr(obj, name, get_config().get_create_config(f"{config_tag}.{name}"))
            return obj
    return inner


def get_input_by_type(name: str, _type: str):
    if not _type or _type == 'str':
        return turtle.textinput(name, f"Please input value for {name}")


def required_config(name: str, _type: str ='str'):
    return config(name, _required_type=_type)


@required_config("ca_file", _type='file')
class CommonConfig(object):
    pass

common_config = CommonConfig()

def get_common_config(name: str) -> str:
    return getattr(common_config, name)

