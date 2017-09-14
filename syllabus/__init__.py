# -*- coding: utf-8 -*-
#
#    This file belongs to the Interactive Syllabus project
#
#    Copyright (C) 2017  Alexandre Dubray, François Michel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



import os
import yaml
from flask import request, has_request_context
from syllabus.utils.yaml_ordered_dict import OrderedDictYAMLLoader
import syllabus.config


def get_toc():
    with open(os.path.join(get_pages_path(), "toc.yaml")) as f:
        return yaml.load(f, OrderedDictYAMLLoader)


def get_root_path():
    return os.path.abspath(os.path.dirname(__file__))


def get_pages_path():
    """
    :return: The path to the content of the "pages" directory. if the syllabus_pages_path variable is set in config.py,
    or if the SYLLABUS_PAGES_PATH environment variable is set in a request context, the returned path will be in the
    specified value (the environment variable has the highest priority)
    If none of these is set, the path will be in the current working directory (os.cwd())
    """
    # first check if the syllabus_pages_path variable is set
    if has_request_context() and "SYLLABUS_PAGES_PATH" in request.environ:
        return request.environ["SYLLABUS_PAGES_PATH"]
    # SYLLABUS_PAGES_PATH can be set by mod_wsgi; If not, the path will be in the current working directory
    path = config.syllabus_pages_path if config.syllabus_pages_path is not None else os.getcwd()
    return os.path.join(path, "pages")
