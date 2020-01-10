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
from flask import request, has_request_context, safe_join
from sphinx.application import Sphinx
from sphinxcontrib.websupport import WebSupport

from syllabus.utils.yaml_ordered_dict import OrderedDictYAMLLoader, OrderedDumper


def get_toc(course, force=False):
    def reload_toc():
        """ loads the TOC explicitely """
        # TODO: change this hack a bit ugly
        from syllabus.utils.toc import TableOfContent
        get_toc.TOC[course] = TableOfContent(course)
        return get_toc.TOC[course]

    if force:
        return reload_toc()
    else:
        # use cached version
        try:
            return get_toc.TOC[course]
        except KeyError:
            return reload_toc()


get_toc.TOC = {}


def save_toc(course, TOC):
    from syllabus.utils.toc import TableOfContent
    """ Dumps the content of the specified TableOfContent in the toc.yaml file. """
    with open(os.path.join(get_pages_path(course), "toc.yaml"), "w") as f:
        yaml.dump(TOC.toc_dict, f, OrderedDumper, default_flow_style=False, allow_unicode=True)


def get_root_path():
    return os.path.abspath(os.path.dirname(__file__))


def get_courses():
    return get_config()['courses'].keys()


def get_pages_path(course):
    """
    :return: The path to the content of the "pages" directory. if the syllabus_pages_path variable is set in config.py,
    or if the SYLLABUS_PAGES_PATH environment variable is set in a request context, the returned path will be in the
    specified value (the environment variable has the highest priority)
    If none of these is set, the path will be in the current working directory (os.cwd())
    """
    syllabus_pages_path = get_config()['courses'][course]['pages']['path']
    path = syllabus_pages_path if syllabus_pages_path is not None else os.getcwd()
    return os.path.join(path, "pages")


def get_pages_cache_path(course):
    """
    :return: The path to the cached version of the "pages" directory. This directory is located inside the "pages"
    directory itself, under the ".cache" name.
    """
    return os.path.join(get_pages_path(course), ".cache")


def remove_no_default_course():
    config = get_config()
    default_course = config['default_course']
    courses_id = list(config['courses'].keys())
    for course_id in courses_id:
        if course_id != default_course:
            del config['courses'][course_id]


def get_config(force=False):
    def reload_config():
        path = get_config_path()
        with open(path, "r") as f:
            get_config.cached = yaml.load(f)
            remove_no_default_course()
            return get_config.cached
    if force:
        return reload_config()
    try:
        return get_config.cached
    except AttributeError:
        return reload_config()


def get_sphinx_build(course, force=False):
    def reload_support():
        config = get_config()['courses'][course]['sphinx']

        # The build dir is created by the Sphinx call. Thus if we need to compile the pages, checking after
        # if the build dir exists would always yield True.
        build_dir_exists = os.path.exists(config['build_dir'])
        app = Sphinx(config["source_dir"], config['conf_dir'] or config["source_dir"], config['build_dir'],
                     os.path.join(config['build_dir'], '.doctrees'), 'html')
        from syllabus.utils import directives
        for directive_name, directive_class in directives.get_directives():
            app.add_directive(directive_name, directive_class)
        if force or not build_dir_exists:
            app.build(False, [])
        if not hasattr(get_sphinx_build, "cached"):
            get_sphinx_build.cached = {}
        get_sphinx_build.cached[course] = app

        return get_sphinx_build.cached[course]
    if force:
        return reload_support()
    try:
        return get_sphinx_build.cached[course]
    except (AttributeError, KeyError):
        return reload_support()


def get_config_path():
    if "SYLLABUS_CONFIG_PATH" in os.environ:
        return os.path.join(os.environ["SYLLABUS_CONFIG_PATH"], "configuration.yaml")
    elif has_request_context() and "SYLLABUS_CONFIG_PATH" in request.environ:
        return os.path.join(request.environ["SYLLABUS_CONFIG_PATH"], "configuration.yaml")
    else:
        return os.path.join(os.path.curdir, "configuration.yaml")


def set_config(config):
    path = get_config_path()
    with open(path, "w") as f:
        if type(config) is str:
            f.write(config)
        else:
            yaml.dump(config, f)
    # update the cached config
    get_config(True)
