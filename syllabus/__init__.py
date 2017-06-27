import os
import yaml
import flask
from syllabus.utils.yaml_ordered_dict import OrderedDictYAMLLoader


def get_toc():
    with open(os.path.join(get_root_path(), "pages", "toc.yaml")) as f:
        return yaml.load(f, OrderedDictYAMLLoader)


def get_root_path():
    return os.path.abspath(os.path.dirname(__file__))
