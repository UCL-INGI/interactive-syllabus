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
import re
import urllib
from urllib import parse
from urllib import request as urllib_request

from docutils.core import publish_string
from docutils.parsers.rst import directives
from flask import Flask, render_template, request, abort, make_response, session, redirect, safe_join, \
    send_from_directory, url_for, render_template_string
from onelogin.saml2.errors import OneLogin_Saml2_Error
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from sqlalchemy.orm.exc import NoResultFound

import syllabus
import syllabus.utils.directives
import syllabus.utils.pages
from syllabus.admin import admin_blueprint, pop_feeback, set_feedback, ErrorFeedback, SuccessFeedback
from syllabus.database import init_db, db_session, update_database, locally_register_new_user, reload_database
from syllabus.models.params import Params
from syllabus.models.user import hash_password, User, UserAlreadyExists
from syllabus.saml import prepare_request, init_saml_auth
from syllabus.utils.inginious_lti import get_lti_data, get_lti_submission
from syllabus.utils.mail import send_confirmation_mail, send_authenticated_confirmation_mail
from syllabus.utils.pages import seeother, get_content_data, permission_admin, update_last_visited, store_last_visited, render_content, default_rst_opts, get_cheat_sheet
from syllabus.utils.toc import Content, Chapter, TableOfContent, ContentNotFoundError, Page

app = Flask(__name__, template_folder=os.path.join(syllabus.get_root_path(), 'templates'),
            static_folder=os.path.join(syllabus.get_root_path(), 'static'))
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
session_sk = syllabus.get_config().get("sessions_secret_key", None)
if session_sk is None or session_sk == "":
    raise Exception("You must give a session secret key to use the application")
app.secret_key = session_sk
directives.register_directive('inginious', syllabus.utils.directives.InginiousDirective)
directives.register_directive('inginious-sandbox', syllabus.utils.directives.InginiousSandboxDirective)
directives.register_directive('table-of-contents', syllabus.utils.directives.ToCDirective)
directives.register_directive('author', syllabus.utils.directives.AuthorDirective)
directives.register_directive('teacher', syllabus.utils.directives.TeacherDirective)
directives.register_directive('framed', syllabus.utils.directives.FramedDirective)
directives.register_directive('print', syllabus.utils.directives.PrintOnlyDirective)


if "saml" in syllabus.get_config()['authentication_methods']:
    saml_config = syllabus.get_config()['authentication_methods']['saml']


@app.route('/', methods=["GET", "POST"])
def index(print=False):
    default_course = syllabus.get_config().get("default_course", None)
    if not default_course:
        return "No default course"
    return redirect(url_for("course_index", course=default_course))


@app.route('/index/<string:course>', methods=["GET", "POST"])
@update_last_visited
def course_index(course, print_mode=False):
    if not course in syllabus.get_config()["courses"].keys():
        abort(404)
    session["course"] = course
    course_config = syllabus.get_config()["courses"][course]
    if course_config.get("sphinx"):
        return seeother("/syllabus/{}/{}".format(course, course_config["sphinx"].get("index_page", "index.html")))
    try:
        TOC = syllabus.get_toc(course)
        if request.args.get("edit") is not None:
            return edit_content(course, TOC.index.path, TOC)
        print_mode = print_mode or request.args.get("print") is not None
        # only display the button to print the whole syllabus in the index
        return render_web_page(course, TOC.index, print_mode=print_mode, display_print_all=True)
    except ContentNotFoundError:
        abort(404)


@app.route('/favicon.ico')
def favicon():
    abort(404)


@app.route('/syllabus/<string:course>/<path:content_path>', methods=["GET", "POST"])
def get_syllabus_content(course, content_path: str, print_mode=False):
    if not course in syllabus.get_config()["courses"].keys():
        abort(404)
    course_config = syllabus.get_config()["courses"][course]
    if course_config["sphinx"]:
        return render_sphinx_page(course, content_path)
    else:
        store_last_visited()
        session["course"] = course
        if content_path[-1] == "/":
            content_path = content_path[:-1]
        TOC = syllabus.get_toc(course)
        if request.args.get("edit") is not None:
            return edit_content(course, content_path, TOC)
        print_mode = print_mode or request.args.get("print") is not None
        try:
            try:
                # assume that it is an RST page
                return render_web_page(course, TOC.get_page_from_path("%s.rst" % content_path), print_mode=print_mode)
            except ContentNotFoundError:
                # it should be a chapter
                # we want to access the index of the chapter
                return render_web_page(course, TOC.get_chapter_from_path(content_path), print_mode=print_mode)
        except ContentNotFoundError:
            abort(404)


# maybe use @cache.cached(timeout=seconds) here
@app.route('/syllabus/<string:course>/assets/<path:asset_path>', methods=["GET", "POST"])
@app.route('/syllabus/<string:course>/<path:content_path>/assets/<path:asset_path>', methods=["GET", "POST"])
def get_syllabus_asset(course, asset_path: str, content_path: str = None):
    if not course in syllabus.get_config()["courses"].keys():
        abort(404)
    session["course"] = course
    TOC = syllabus.get_toc(course)
    if content_path is None:
        return send_from_directory(TOC.get_global_asset_directory(), asset_path)
    if content_path[-1] == "/":
        content_path = content_path[:-1]
    try:
        # explicitly check that the chapter exists
        chapter = TOC.get_chapter_from_path(content_path)
        # secured way to serve a static file
        # TODO: use X-Sendfile with this method to be efficient
        return send_from_directory(TOC.get_asset_directory(chapter), asset_path)
    except ContentNotFoundError:
        abort(404)


@app.route('/preview/<string:course>/refresh', methods=["POST"])
@permission_admin
def refresh(course):
    TOC = syllabus.get_toc(course)
    data = request.form['content']
    config = syllabus.get_config()
    inginious_config = config['courses'][course]['inginious']
    inginious_course_url = "%s/%s" % (inginious_config['url'], inginious_config['course_id'])
    path = safe_join(inginious_config.get("simple_grader_pattern", "/"), inginious_config['course_id'])
    inginious_sandbox_url = urllib.parse.urljoin(inginious_config["url"], path)
    same_origin_proxy = inginious_config['same_origin_proxy']
    code_html = render_template_string(publish_string(data, writer_name='html', settings_overrides=default_rst_opts),
                                 logged_in=session.get("user", None),
                                 inginious_sandbox_url=inginious_sandbox_url,
                                 inginious_course_url=inginious_course_url if not same_origin_proxy else ("/postinginious/" + course),
                                 inginious_url=inginious_config['url'], this_content=data,
                                 render_rst=lambda content, **kwargs: syllabus.utils.pages.render_content(course, content, **kwargs),
                                 course_str=course,
                                 courses_titles={course: config["courses"][course]["title"] for course in syllabus.get_courses()},
                                 toc=TOC,
                                 get_lti_data=get_lti_data, get_lti_submission=get_lti_submission,
                                 render_rst_str=syllabus.utils.pages.render_rst_str)
    return "<div id=\"preview\" style=\"overflow-y: scroll\">"+code_html+"</div>"


@app.route('/preview/cheat_sheet', methods=["GET"])
@permission_admin
def render_cheat_sheet():
    return get_cheat_sheet()


@permission_admin
@update_last_visited
def edit_content(course, content_path, TOC: TableOfContent):
    try:
        content = TOC.get_page_from_path("%s.rst" % content_path)
    except ContentNotFoundError:
        content = TOC.get_content_from_path(content_path)
    if request.method == "POST":
        inpt = request.form
        if "new_content" not in inpt:
            return seeother(request.path)
        else:
            if type(content) is Chapter:
                with open(safe_join(syllabus.get_pages_path(course), content.path, "chapter_introduction.rst"), "w") as f:
                    f.write(inpt["new_content"])
            else:
                with open(safe_join(syllabus.get_pages_path(course), content.path), "w") as f:
                    f.write(inpt["new_content"])
            return seeother(request.path)
    elif request.method == "GET":
        return render_template("edit_page.html", course=course, content_data=get_content_data(course, content),
                               content=content, TOC=TOC, cheat_sheet=get_cheat_sheet(), enable_preview=syllabus.get_config().get("enable_editing_preview", False))


def render_web_page(course: str, content: Content, print_mode=False, display_print_all=False):
    try:
        TOC = syllabus.get_toc(course)
        session["print_mode"] = print_mode
        try:
            previous = TOC.get_previous_content(content)
        except KeyError:
            previous = None
        try:
            next = TOC.get_next_content(content)
        except KeyError:
            next = None

        config = syllabus.get_config()
        inginious_config = config['courses'][course]['inginious']
        inginious_course_url = "%s/%s" % (inginious_config['url'], inginious_config['course_id'])
        path = safe_join(inginious_config.get("simple_grader_pattern", "/"), inginious_config['course_id'])
        inginious_sandbox_url = urllib.parse.urljoin(inginious_config["url"], path)
        same_origin_proxy = inginious_config['same_origin_proxy']
        retval = render_template('rst_page.html' if not print_mode else 'print_page.html',
                                 logged_in=session.get("user", None),
                                 inginious_config = syllabus.get_config()['courses'][course]['inginious'],
                                 inginious_course_url=inginious_course_url if not same_origin_proxy else ("/postinginious/" + course),
                                 inginious_sandbox_url=inginious_sandbox_url,
                                 inginious_url=inginious_config['url'],
                                 containing_chapters=TOC.get_containing_chapters_of(content), this_content=content,
                                 render_rst=lambda content, **kwargs: syllabus.utils.pages.render_content(course, content, **kwargs),
                                 render_footer= lambda course: syllabus.utils.pages.render_footer(course),
                                 content_at_same_level=TOC.get_content_at_same_level(content),
                                 course_str=course,
                                 courses_titles={course: config["courses"][course]["title"] for course in syllabus.get_courses()},
                                 toc=TOC,
                                 direct_content=TOC.get_direct_content_of(content), next=next, previous=previous,
                                 display_print_all=display_print_all,
                                 get_lti_data=get_lti_data, get_lti_submission=get_lti_submission,
                                 render_rst_str=syllabus.utils.pages.render_rst_str)

        session["print_mode"] = False
    except Exception:
        # ensure that the print mode is disabled
        session["print_mode"] = False
        raise
    return retval

def render_sphinx_page(course: str, docname: str):
    build = syllabus.get_sphinx_build(course)
    if docname.endswith(".html"):
        doc_path = safe_join(build.builder.outdir, docname)
        config = syllabus.get_config()
        inginious_config = config['courses'][course]['inginious']
        inginious_course_url = "%s/%s" % (inginious_config['url'], inginious_config['course_id'])
        path = safe_join(inginious_config.get("simple_grader_pattern", "/"), inginious_config['course_id'])
        inginious_sandbox_url = urllib.parse.urljoin(inginious_config["url"], path)
        same_origin_proxy = inginious_config['same_origin_proxy']
        try:
            with open(doc_path) as f:
                store_last_visited()
                return render_template_string('{{% extends "sphinx_page.html" %}} {{% block content %}}{}{{% endblock %}}'.format(f.read()),
                                         logged_in=session.get("user", None),
                                         inginious_course_url=inginious_course_url if not same_origin_proxy else (
                                                     "/postinginious/" + course),
                                         inginious_sandbox_url=inginious_sandbox_url,
                                         courses_titles={course: config["courses"][course]["title"] for course in
                                                         syllabus.get_courses()},
                                         inginious_config=inginious_config,
                                         inginious_url=inginious_config['url'],
                                         course_str=course,
                                         get_lti_data=get_lti_data, get_lti_submission=get_lti_submission)
        except FileNotFoundError:
            abort(404)
    return send_from_directory(build.builder.outdir, docname)

@app.route('/postinginious/<string:course>', methods=['POST'])
def post_inginious(course):
    inpt = request.form
    data = parse.urlencode(inpt).encode()
    inginious_config = syllabus.get_config()['courses'][course]['inginious']
    path = safe_join(inginious_config.get("simple_grader_pattern", "/"), inginious_config['course_id'])
    inginious_sandbox_url = urllib.parse.urljoin(inginious_config["url"], path)
    req = urllib_request.Request(inginious_sandbox_url, data=data)
    resp = urllib_request.urlopen(req)
    response = make_response(resp.read().decode())
    response.headers['Content-Type'] = 'text/json'
    return response


@app.route('/parserst', methods=['POST'])
def parse_rst():
    inpt = request.form["rst"]
    out = publish_string(inpt, writer_name='html')
    return out


@app.route('/update_pages/<string:secret>/<string:course>', methods=['GET', 'POST'])
def update_pages(secret, course):
    params = Params.query.one()
    if secret != params.git_hook_url or 'git' not in syllabus.get_config()['courses'][course]['pages']:
        return seeother("/")
    syllabus.utils.pages.init_and_sync_repo(course, force_sync=True)
    return "done"


def main():
    update_database()
    reload_database()
    init_db()
    app.run(host='0.0.0.0', port=5000)
