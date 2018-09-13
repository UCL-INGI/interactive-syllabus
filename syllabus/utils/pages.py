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


def get_chapter_intro(course, chapter):
    try:
        with open(safe_join(syllabus.get_pages_path(course), chapter.path, "chapter_introduction.rst"), 'r', encoding="utf-8") as f:
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


def render_content(course, content, **kwargs):
    if type(content) is Chapter:
        return render_rst_file(course, "chapter_index.rst", chapter_path=content.path,
                               chapter_desc=get_chapter_intro(course, content), **kwargs)
    else:
        return render_rst_file(course, content.path, **kwargs)


def render_rst_file(course, page_path, **kwargs):
    with open(safe_join(syllabus.get_pages_path(course), page_path), "r") as f:
        # TODO: cache the return value of publish_string, it should not change per user
        return render_template_string(publish_string(f.read(), writer_name='html', settings_overrides=default_rst_opts),
                               **kwargs)

def get_content_data(course, content: Content):
    path = content.path if type(content) is Page else safe_join(content.path, "chapter_introduction.rst")
    try:
        with open(safe_join(syllabus.get_pages_path(course), path), "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def generate_toc_yaml(course):
    def create_dict(path, name):
        retval = {"title": name, "content": {}}
        for entry in os.listdir(path):
            if entry[0] != ".":
                if os.path.isdir(os.path.join(path, entry)):
                    retval["content"][entry] = create_dict(os.path.join(path, entry), entry)
                elif entry[-4:] == ".rst" and entry not in ["chapter_introduction.rst"]:
                    retval["content"][entry] = {"title": entry[:-4]}
        return retval

    path = syllabus.get_pages_path(course)
    result = {}
    for dir in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
        result[dir] = create_dict(os.path.join(path, dir), dir)
    return str(yaml.dump(result))


def init_and_sync_repo(course, force_sync=False):
    """
    Initializes a git repository in the pages folder if no repository already exists, then
    synchronizes it with the remote specified in the configuration file if the
    origin didn't exist before or if force_sync is True.
    Warning: the local changes will be overwritten.
    :return:
    """
    path = os.path.join(syllabus.get_root_path(), syllabus.get_pages_path(course))
    git_config = syllabus.get_config()['courses'][course]['pages']['git']
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        repo = Repo(path)
    except InvalidGitRepositoryError:
        # this is currently not a git repo
        repo = Repo.init(path)
    try:
        origin = repo.remote("origin").set_url(git_config['remote'])
    except:
        origin = repo.create_remote("origin", git_config['remote'])
        # sync the repo if the origin wasn't already there
        force_sync = True
    if force_sync:
        git_force_sync(course, origin, repo)
        syllabus.get_toc(course, True)


def git_force_sync(course, origin, repo):
    git_config = syllabus.get_config()['courses'][course]['pages']['git']
    private_key_path = git_config['repository_private_key']
    branch = git_config['branch']
    if private_key_path is not None:
        # We need to be compatible with git < 2.3 as CentOS7 uses an older version, so here is an ugly code
        # to use a deployment key that will work with old git versions

        # set the ssh executable
        ssh_executable_path = os.path.join(syllabus.get_root_path(), "ssh_executable.sh")
        with open(ssh_executable_path, "w") as f:
            f.write('#!/bin/sh\nID_RSA=%s\nssh -o StrictHostKeyChecking=no -i $ID_RSA "$@"' % private_key_path)
        os.system("chmod +x %s" % ssh_executable_path)
        with repo.git.custom_environment(GIT_SSH=ssh_executable_path):
            origin.fetch()
            # complete synchronization (local changes will be overwritten)
            repo.git.reset('--hard', 'origin/%s' % branch)
        # Hereunder is a more pretty version, uncomment it when the git version is >= 2.3
        # with repo.git.custom_environment(GIT_SSH_COMMAND='ssh -i %s -o StrictHostKeyChecking=no' % private_key_path):
        #     origin.fetch()
        #     # complete synchronization (local changes will be overwritten)
        #     repo.git.reset('--hard', 'origin/%s' % branch)
    else:
        origin.fetch()
        # complete synchronization (local changes will be overwritten)
        repo.git.reset('--hard', 'origin/%s' % branch)
