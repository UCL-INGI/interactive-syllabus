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


def get_toc():
    with open(os.path.join(get_pages_path(), "toc.yaml")) as f:
        return yaml.load(f, OrderedDictYAMLLoader)


def get_root_path():
    return os.path.abspath(os.path.dirname(__file__))


def get_pages_path():
    """
    :return: The path to the content of the "pages" directory
    """
    # SYLLABUS_PAGES_PATH can be set by mod_wsgi
    path = request.environ.get("SYLLABUS_PAGES_PATH", os.getcwd()) if has_request_context() else os.getcwd()
    return os.path.join(path, "pages")
