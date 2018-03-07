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
from functools import wraps

import yaml
from docutils.core import publish_string
from flask import render_template_string, redirect, session, abort
from flask.helpers import safe_join
from git import Repo, InvalidGitRepositoryError
from werkzeug.utils import secure_filename

import syllabus
from syllabus.models.user import User
from syllabus.utils.feedbacks import set_feedback
from syllabus.utils.toc import Chapter, Content, Page

default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'output_encoding': 'unicode',
    'input_encoding': 'unicode',
    'traceback': True,
    'halt_level': 5
}


def seeother(link, feedback=None):
    if feedback is not None:
        set_feedback(session, feedback)
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


def permission_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        username = session["user"]["username"] if "user" in session else None
        if username is None:
            abort(403)
        user = User.query.filter(User.username == username).first()
        if not user.admin:
            abort(403)
        return f(*args, **kwargs)
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


def get_content_data(content: Content):
    path = content.path if type(content) is Page else safe_join(content.path, "chapter_introduction.rst")
    try:
        with open(safe_join(syllabus.get_pages_path(), path), "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def generate_toc_yaml():
    def create_dict(path, name):
        retval = {"title": name, "content": {}}
        for entry in os.listdir(path):
            if entry[0] != ".":
                if os.path.isdir(os.path.join(path, entry)):
                    retval["content"][entry] = create_dict(os.path.join(path, entry), entry)
                elif entry[-4:] == ".rst" and entry not in ["chapter_introduction.rst"]:
                    retval["content"][entry] = {"title": entry[:-4]}
        return retval

    path = syllabus.get_pages_path()
    result = {}
    for dir in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
        result[dir] = create_dict(os.path.join(path, dir), dir)
    return str(yaml.dump(result))


def init_and_sync_repo(force_sync=False):
    """
    Initializes a git repository in the pages folder if no repository already exists, then
    synchronizes it with the remote specified in config.syllabus_pages_repo_remote if the
    origin didn't exist before or if force_sync is True.
    Warning: the local changes will be overwritten.
    :return:
    """
    path = os.path.join(syllabus.get_root_path(), syllabus.get_pages_path())
    try:
        repo = Repo(path)
    except InvalidGitRepositoryError:
        # this is currently not a git repo
        repo = Repo.init(path)
    try:
        origin = repo.remote("origin").set_url(syllabus.config.syllabus_pages_repo_remote)
    except:
        origin = repo.create_remote("origin", syllabus.config.syllabus_pages_repo_remote)
        # sync the repo if the origin wasn't already there
        force_sync = True
    if force_sync:
        git_force_sync(origin, repo)


def git_force_sync(origin, repo: Repo):
    if syllabus.config.repo_private_key is not None:
        with repo.git.custom_environment(GIT_SSH_COMMAND='ssh -i %s -o StrictHostKeyChecking=no' % syllabus.config.repo_private_key):
            origin.fetch("master")
            # complete synchronization (local changes will be overwritten)
            repo.git.reset('--hard', 'origin/master')
    else:
        origin.fetch("master")
        # complete synchronization (local changes will be overwritten)
        repo.git.reset('--hard', 'origin/master')
