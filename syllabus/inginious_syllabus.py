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

import yaml
from docutils.core import publish_string
from docutils.parsers.rst import directives
from flask import Flask, render_template, request, abort, make_response, session, redirect
from onelogin.saml2.utils import OneLogin_Saml2_Utils

import syllabus
import syllabus.utils.directives
import syllabus.utils.pages
from syllabus.admin import admin_blueprint
from syllabus.config import *
from syllabus.database import init_db, db_session, update_database
from syllabus.models.user import hash_password, User
from syllabus.saml import prepare_request, init_saml_auth
from syllabus.utils.pages import seeother, get_content_data, permission_admin
from syllabus.utils.toc import Content, Chapter, TableOfContent, Page, ContentNotFoundError

app = Flask(__name__, template_folder=os.path.join(syllabus.get_root_path(), 'templates'),
            static_folder=os.path.join(syllabus.get_root_path(), 'static'))
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
directives.register_directive('inginious', syllabus.utils.directives.InginiousDirective)
directives.register_directive('inginious-sandbox', syllabus.utils.directives.InginiousSandboxDirective)
directives.register_directive('table-of-contents', syllabus.utils.directives.ToCDirective)
directives.register_directive('author', syllabus.utils.directives.AuthorDirective)


if "saml" in authentication_methods:
    with open(os.path.join(syllabus.get_root_path(), "saml", "saml.yaml")) as f:
        saml_config = yaml.load(f)


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    TOC = syllabus.get_toc()
    if request.args.get("edit") is not None:
        return edit_content(TOC.index.path, TOC)
    try:
        return render_web_page(TOC.index, print_mode=request.args.get("print") is not None)
    except ContentNotFoundError:
        abort(404)


@app.route('/favicon.ico')
def favicon():
    abort(404)


@app.route('/syllabus/<path:content_path>', methods=["GET", "POST"])
def get_syllabus_content(content_path: str, print=False):
    if content_path[-1] == "/":
        content_path = content_path[:-1]
    TOC = syllabus.get_toc()
    if request.args.get("edit") is not None:
        return edit_content(content_path, TOC)
    print_mode = print or request.args.get("print") is not None
    try:
        try:
            # assume that it is an RST page
            return render_web_page(TOC.get_page_from_path("%s.rst" % content_path), print_mode=print_mode)
        except ContentNotFoundError:
            # it should be a chapter
            if request.args.get("print") == "all_content":
                # we want to print all the content of the chapter
                return get_chapter_printable_content(TOC.get_chapter_from_path(content_path), TOC)
            # we want to access the index of the chapter
            return render_web_page(TOC.get_chapter_from_path(content_path), print_mode=print_mode)
    except ContentNotFoundError:
        abort(404)


@permission_admin
def edit_content(content_path, TOC: TableOfContent):
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
                with open(os.path.join(syllabus.get_pages_path(), content.path, "chapter_introduction.rst"), "w") as f:
                    f.write(inpt["new_content"])
            else:
                with open(os.path.join(syllabus.get_pages_path(), content.path), "w") as f:
                    f.write(inpt["new_content"])
            return seeother(request.path)
    elif request.method == "GET":
        return render_template("edit_page.html", content_data=get_content_data(content), content=content, TOC=TOC)


def get_chapter_printable_content(chapter: Chapter, toc: TableOfContent):
    def fetch_content(chapter):
        printable_content = [chapter]
        for content in toc.get_direct_content_of(chapter):
            if type(content) is Chapter:
                printable_content += fetch_content(content)
            else:
                printable_content.append(content)
        return printable_content
    return render_template("print_full_chapter_content.html", chapter=fetch_content(chapter),
                           render_rst=syllabus.utils.pages.render_content)


def render_web_page(content: Content, print_mode=False):
    try:
        TOC = syllabus.get_toc()
        session["print_mode"] = print_mode
        try:
            previous = TOC.get_previous_content(content)
        except KeyError:
            previous = None
        try:
            next = TOC.get_next_content(content)
        except KeyError:
            next = None
        retval = render_template('rst_page.html' if not print_mode else 'print_page.html',
                                 logged_in=session.get("user", None),
                                 inginious_url=inginious_course_url if not same_origin_proxy else "/postinginious",
                                 containing_chapters=TOC.get_containing_chapters_of(content), this_content=content,
                                 render_rst=syllabus.utils.pages.render_content,
                                 content_at_same_level=TOC.get_content_at_same_level(content),
                                 toc=TOC,
                                 direct_content=TOC.get_direct_content_of(content), next=next, previous=previous)

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
        return render_template("login.html", auth_methods=authentication_methods)
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
        if saml:
            req = prepare_request(request)
            auth = init_saml_auth(req, saml_config)
            return redirect(auth.logout())
    return seeother('/')


@app.route('/postinginious', methods=['POST'])
def post_inginious():
    inpt = request.form
    data = parse.urlencode(inpt).encode()
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
    if "saml" not in authentication_methods:
        abort(404)
    req = prepare_request(request)
    req['request_uri'] = request.path  # hack to ensure to have the correct path and to avoid RelayState loops
    auth = init_saml_auth(req, saml_config)

    # if 'sso' in request.args:
    #     return
    if request.method == "GET":
        return redirect(auth.login())
    elif 'acs' in request.args:
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

            session["user"] = user.to_dict() + {"login_method": "saml"}

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


def main():
    update_database()
    init_db()
    app.run(host='0.0.0.0', port=5000)
