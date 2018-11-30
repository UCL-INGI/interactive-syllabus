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
from urllib import parse
from urllib import request as urllib_request

from docutils.core import publish_string
from docutils.parsers.rst import directives
from flask import Flask, render_template, request, abort, make_response, session, redirect, safe_join, \
    send_from_directory, url_for, render_template_string
from onelogin.saml2.errors import OneLogin_Saml2_Error
from onelogin.saml2.utils import OneLogin_Saml2_Utils

import syllabus
import syllabus.utils.directives
import syllabus.utils.pages
from syllabus.admin import admin_blueprint
from syllabus.database import init_db, db_session, update_database
from syllabus.models.params import Params
from syllabus.models.user import hash_password, User
from syllabus.saml import prepare_request, init_saml_auth
from syllabus.utils.inginious_lti import get_lti_data, get_lti_submission
from syllabus.utils.pages import seeother, get_content_data, permission_admin, render_content, default_rst_opts, get_cheat_sheet
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
    saml_config = syllabus.get_config()['saml']


@app.route('/', methods=["GET", "POST"])
def index(print=False):
    default_course = syllabus.get_config().get("default_course", None)
    if not default_course:
        return "No default course"
    return redirect(url_for("course_index", course=default_course))


@app.route('/index/<string:course>', methods=["GET", "POST"])
def course_index(course, print_mode=False):
    if not course in syllabus.get_config()["courses"].keys():
        abort(404)
    session["course"] = course
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
            if request.args.get("print") == "all_content":
                # we want to print all the content of the chapter
                return get_chapter_printable_content(course, TOC.get_chapter_from_path(content_path), TOC)
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
    same_origin_proxy = inginious_config['same_origin_proxy']
    code_html = render_template_string(publish_string(data, writer_name='html', settings_overrides=default_rst_opts),
                                 logged_in=session.get("user", None),
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


@app.route('/print_all/<string:course>')
def print_all_syllabus(course):
    if not course in syllabus.get_config()["courses"].keys():
        abort(404)
    session["course"] = course
    TOC = syllabus.get_toc(course)
    session["print_mode"] = True

    retval = render_template("print_multiple_contents.html", contents=TOC,
                             render_rst=lambda content, **kwargs: syllabus.utils.pages.render_content(course, content, **kwargs),
                             toc=TOC, get_lti_data=get_lti_data,
                             get_lti_submission=get_lti_submission, logged_in=session.get("user", None),
                             course_str=course,
                             render_rst_str=syllabus.utils.pages.render_rst_str)
    session["print_mode"] = False
    return retval


def get_chapter_printable_content(course: str, chapter: Chapter, toc: TableOfContent):
    TOC = syllabus.get_toc(course)
    def fetch_content(chapter):
        printable_content = [chapter]
        for content in toc.get_direct_content_of(chapter):
            if type(content) is Chapter:
                printable_content += fetch_content(content)
            else:
                printable_content.append(content)
        return printable_content

    session["print_mode"] = True
    try:
        retval = render_template("print_multiple_contents.html", contents=fetch_content(chapter),
                                 render_rst=lambda content, **kwargs: syllabus.utils.pages.render_content(course, content, **kwargs),
                                 toc=TOC,
                                 course_str=course)
        session["print_mode"] = False
        return retval
    except:
        session["print_mode"] = False
        raise


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
        same_origin_proxy = inginious_config['same_origin_proxy']
        retval = render_template('rst_page.html' if not print_mode else 'print_page.html',
                                 logged_in=session.get("user", None),
                                 inginious_course_url=inginious_course_url if not same_origin_proxy else ("/postinginious/" + course),
                                 inginious_url=inginious_config['url'],
                                 containing_chapters=TOC.get_containing_chapters_of(content), this_content=content,
                                 render_rst=lambda content, **kwargs: syllabus.utils.pages.render_content(course, content, **kwargs),
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


@app.route("/resetpassword/<secret>", methods=["GET", "POST"])
def reset_password(secret):
    user = db_session.query(User).filter(User.change_password_url == secret).first()
    if user is None:
        # TODO: log
        return seeother("/")
    if request.method == "GET":
        return render_template("reset_password.html", alert_hidden=True)
    if request.method == "POST":
        inpt = request.form
        password = inpt["password"]
        password_confirm = inpt["password_confirm"]
        if password != password_confirm:
            return render_template("reset_password.html", alert_hidden=False)
        password_hash = hash_password(password.encode("utf-8"))
        user.hash_password = password_hash
        user.change_password_url = None
        db_session.commit()
        return seeother("/login")


@app.route("/login", methods=['GET', 'POST'])
def log_in():
    if request.method == "GET":
        return render_template("login.html", auth_methods=syllabus.get_config()['authentication_methods'])
    if request.method == "POST":
        inpt = request.form
        username = inpt["username"]
        password = inpt["password"]
        try:
            password_hash = hash_password(password.encode("utf-8"))
        except UnicodeEncodeError:
            # TODO: log
            return seeother("/login")

        user = User.query.filter(User.username == username).first()
        if user is None or user.hash_password != password_hash:
            abort(403)
        session['user'] = user.to_dict()
        return seeother('/')


@app.route("/logout")
def log_out():
    if "user" in session:
        saml = session["user"].get("login_method", None) == "saml"
        session.pop("user", None)
        if saml and "singleLogoutService" in saml_config["sp"]:
            try:
                req = prepare_request(request)
                auth = init_saml_auth(req, saml_config)
                return redirect(auth.logout())
            except OneLogin_Saml2_Error:
                pass
    return seeother('/')


@app.route('/postinginious/<string:course>', methods=['POST'])
def post_inginious(course):
    inpt = request.form
    data = parse.urlencode(inpt).encode()
    inginious_config = syllabus.get_config()['courses'][course]['inginious']
    inginious_course_url = "%s/%s" % (inginious_config['url'], inginious_config['course_id'])
    req = urllib_request.Request(inginious_course_url, data=data)
    resp = urllib_request.urlopen(req)
    response = make_response(resp.read().decode())
    response.headers['Content-Type'] = 'text/json'
    return response


@app.route('/parserst', methods=['POST'])
def parse_rst():
    inpt = request.form["rst"]
    out = publish_string(inpt, writer_name='html')
    return out


@app.route('/saml', methods=['GET', 'POST'])
def saml():
    if "saml" not in syllabus.get_config()['authentication_methods']:
        abort(404)
    req = prepare_request(request)
    req['request_uri'] = request.path  # hack to ensure to have the correct path and to avoid RelayState loops
    auth = init_saml_auth(req, saml_config)

    # if 'sso' in request.args:
    #     return
    if request.method == "GET":
        return redirect(auth.login())
    else:
        auth.process_response()
        errors = auth.get_errors()
        # Try and check if IdP is using several signature certificates
        # This is a limitation of python3-saml
        for cert in saml_config["idp"].get("additionalX509certs", []):
            if auth.get_last_error_reason() == "Signature validation failed. SAML Response rejected":
                import copy
                # Change used IdP certificate
                new_settings = copy.deepcopy(saml_config)
                new_settings["idp"]["x509cert"] = cert
                # Retry processing response
                auth = init_saml_auth(req, new_settings)
                auth.process_response()
                errors = auth.get_errors()
        if len(errors) == 0:
            attrs = auth.get_attributes()
            # session['samlNameId'] = auth.get_nameid()
            # session['samlSessionIndex'] = auth.get_session_index()

            username = attrs[saml_config['sp']['attrs']['username']][0]
            realname = attrs[saml_config['sp']['attrs']['realname']][0]
            email = attrs[saml_config['sp']['attrs']['email']][0]

            user = User.query.filter(User.email == email).first()

            if user is None:  # The user does not exist in our DB
                user = User(name=username, full_name=realname, email=email, hash_password=None,
                            change_password_url=None)
                db_session.add(user)
                db_session.commit()

            session["user"] = user.to_dict()
            session["user"].update({"login_method": "saml"})

            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if 'RelayState' in request.form and self_url != request.form['RelayState']:
                return redirect(auth.redirect_to(request.form['RelayState']))

    return seeother("/")


@app.route('/saml/metadata/')
def metadata():
    req = prepare_request(request)
    auth = init_saml_auth(req, saml_config)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp


@app.route('/update_pages/<string:secret>/<string:course>', methods=['GET', 'POST'])
def update_pages(secret, course):
    params = Params.query.one()
    if secret != params.git_hook_url or 'git' not in syllabus.get_config()['courses'][course]['pages']:
        return seeother("/")
    syllabus.utils.pages.init_and_sync_repo(course, force_sync=True)
    return "done"


def main():
    update_database()
    init_db()
    app.run(host='0.0.0.0', port=5000)
