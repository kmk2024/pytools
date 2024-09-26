# -*- coding: utf-8 -*-
import os
from functools import reduce
from tkinter import simpledialog, filedialog

import yaml


try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Config(object):
    config_path: str
    config_dict: dict

    def __init__(self, config_path: str = f"{os.path.dirname(os.path.realpath(__file__))}/pytools/config.yaml") -> None:
        self.config_path = config_path
        self.refresh_config()

    def refresh_config(self) -> dict:
        dir_name = os.path.dirname(self.config_path)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        try:
            f = open(self.config_path)
            self.config_dict = yaml.load(f, Loader=Loader)
            if not self.config_dict:
                self.config_dict = dict()
        except FileNotFoundError:
            self.config_dict = dict()
        return self.config_dict

    def get_config(self, property_key: str, default_value=None) -> object:
        try:
            return reduce(lambda c, k: c[k], property_key.split('.'), self.config_dict)
        except:
            return default_value

    def get_create_config(self, property_key: str, default_value: object, required_type: str =None) -> Object:
        _value = self.get_config(property_key)
        if not _value:
            _value = default_value
            if not _value:
                if required_type == 'str':
                    _value = simpledialog.askstring(property_key, f"Please input value for {property_key}")
                elif required_type == 'file':
                    _value = filedialog.askopenfilename(title=f"Please select file for {property_key}")
                else:
                    assert f'not supported type{required_type}'
                assert not _value, f"{property_key} is none"
            self.update_config(property_key, _value)
        return _value

    def dump_config(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_dict, f)

    def update_config(self, property_key: str, value: object) -> object:
        keys = property_key.split('.')
        lens = len(keys)
        config_value: dict = self.config_dict
        for i in range(lens):
            key = keys[i]
            if i == lens - 1:
                config_value[key] = value
            else:
                new_value = config_value.get(key)
                if not new_value:
                    new_value = dict()
                    config_value[key] = new_value
                config_value = new_value
        self.dump_config()
        return value


if __name__ == '__main__':
    config = Config()
    print(config.get_config("a"))