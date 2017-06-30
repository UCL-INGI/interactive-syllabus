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
from collections import OrderedDict

import sys
from docutils.core import publish_string
from flask.helpers import get_root_path
from flask import render_template_string
from werkzeug.utils import secure_filename

import syllabus
from syllabus.config import *
import syllabus.utils.directives as directives
from syllabus.utils import rst

default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'output_encoding': 'unicode',
    'input_encoding': 'unicode',
    'traceback': True,
    'halt_level': 5
}

def get_syllabus_toc(wanted_root):
    """
    :param wanted_root: The directory from where the arborescence will start
    :return: An ordered dictionary containing the table of content of the syllabus.
    The chapters and pages inside chapters are ordered in lexicographical order
    """
    structure = OrderedDict()
    root_path = get_root_path("syllabus")
    for directory in sorted(os.listdir(os.path.join(root_path, wanted_root))):
        current_path = os.path.join(root_path, wanted_root, directory)
        if os.path.isdir(current_path):
            structure[directory] = get_syllabus_toc(os.path.join(wanted_root, directory))
        else:
            structure[directory.replace('.rst', '')] = OrderedDict()
    return structure


def get_chapter_content(chapter_name, toc=None):
    toc = syllabus.get_toc() if toc is None else toc
    return toc[chapter_name]


def get_chapter_desc(chapter_name, toc):
    file = toc[chapter_name].get("chapter_intro_file")
    if file is not None:
        with open(os.path.join(syllabus.get_root_path(), "pages", chapter_name, file), 'r', encoding="utf-8") as f:
            return f.read()
    return ""


def sanitize_filenames(f):
    def wrapper(chapter, page, **kwargs):
        return f(secure_filename(chapter), secure_filename(page) if page is not None else page, **kwargs)

    return wrapper


@sanitize_filenames
def render_page(chapter, page=None, toc=syllabus.get_toc()):
    if page is None:
        return render_rst_file("chapter_index.rst", chapter_name=chapter,
                               chapter_desc=get_chapter_desc(chapter, toc))
    else:
        return render_rst_file(os.path.join(chapter, "%s.rst" % page))


def render_rst_file(page_path, **kwargs):
    root_path = get_root_path("syllabus")
    with open(os.path.join(root_path, "pages", page_path), "r") as f:
        return publish_string(render_template_string(f.read(), **kwargs),
                              writer_name='html', settings_overrides=default_rst_opts)
