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


from docutils.core import publish_string
from flask import render_template_string, redirect
from flask.helpers import safe_join
from werkzeug.utils import secure_filename

import syllabus
from syllabus.utils.toc import Chapter

default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'output_encoding': 'unicode',
    'input_encoding': 'unicode',
    'traceback': True,
    'halt_level': 5
}


def seeother(link):
    return redirect(link, code=303)


def get_chapter_intro(chapter):
    try:
        with open(safe_join(syllabus.get_pages_path(), chapter.path, "chapter_introduction.rst"), 'r', encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def sanitize_filenames(f):
    def wrapper(chapter, page, **kwargs):
        return f(secure_filename(chapter), secure_filename(page) if page is not None else page, **kwargs)

    return wrapper


def sanitize_path(f):
    def wrapper(content_path, **kwargs):
        return f(secure_filename(content_path), **kwargs)
    return wrapper


def render_content(content):
    if type(content) is Chapter:
        return render_rst_file("chapter_index.rst", chapter_path=content.path,
                               chapter_desc=get_chapter_intro(content))
    else:
        return render_rst_file(content.path)


def render_rst_file(page_path, **kwargs):
    with open(safe_join(syllabus.get_pages_path(), page_path), "r") as f:
        return publish_string(render_template_string(f.read(), **kwargs),
                              writer_name='html', settings_overrides=default_rst_opts)
