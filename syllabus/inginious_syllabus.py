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
import json
import os

import yaml
from flask import Flask, render_template, request, abort, make_response, session, redirect
from onelogin.saml2.utils import OneLogin_Saml2_Utils

import syllabus.utils.pages, syllabus.utils.directives
from syllabus.database import init_db, db_session
from syllabus.models.user import hash_password, User
from syllabus.saml import prepare_request, init_saml_auth
from syllabus.utils.pages import get_chapter_content, seeother
from docutils.core import publish_string
from syllabus.config import *
import syllabus
from docutils.parsers.rst import directives
from urllib import parse
from urllib import request as urllib_request

app = Flask(__name__, template_folder=os.path.join(syllabus.get_root_path(), 'templates'),
            static_folder=os.path.join(syllabus.get_root_path(), 'static'))
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
directives.register_directive('inginious', syllabus.utils.directives.InginiousDirective)
directives.register_directive('table-of-contents', syllabus.utils.directives.ToCDirective)
directives.register_directive('author', syllabus.utils.directives.AuthorDirective)

if "saml" in authentication_methods:
    with open(os.path.join(syllabus.get_root_path(), "saml", "saml.yaml")) as f:
        saml_config = yaml.load(f)

@app.route('/')
@app.route('/index')
def index():
    toc = syllabus.get_toc()
    try:
        return render_template('rst_page.html', logged_in=session.get("user", None),
                               inginious_url=inginious_course_url if not same_origin_proxy else "/postinginious",
                               chapter="", page="index", render_rst=syllabus.utils.pages.render_page,
                               structure=syllabus.get_toc(), list=list,
                               toc=toc,
                               chapter_content=None, next=None, previous=None)
    except FileNotFoundError:
        abort(404)


@app.route('/favicon.ico')
def favicon():
    abort(404)


@app.route('/<chapter>')
def chapter_index(chapter):
    try:
        return render_web_page(chapter, None)
    except ValueError:
        abort(404)


@app.route('/<chapter>/<page>')
@syllabus.utils.pages.sanitize_filenames
def get_page(chapter, page):
    try:
        return render_web_page(chapter, page)
    except FileNotFoundError:
        abort(404)


def render_web_page(chapter, page):
    toc = syllabus.get_toc()
    # find previous/next page/chapter
    if page is None:
        # find previous/next chapter
        chapters = list(toc.keys())
        chapter_index = chapters.index(chapter)
        previous = None if chapter_index == 0 else chapters[chapter_index - 1]
        next = None if chapter_index == len(chapters) - 1 else chapters[chapter_index + 1]
    else:
        # find previous/next page
        pages = list(toc[chapter]["content"].keys())
        page_index = pages.index(page)
        previous = None if page_index == 0 else pages[page_index - 1]
        next = None if page_index == len(pages) - 1 else pages[page_index + 1]
    return render_template('rst_page.html', logged_in=session.get("user", None),
                           inginious_url=inginious_course_url if not same_origin_proxy else "/postinginious",
                           chapter=chapter, page=page, render_rst=syllabus.utils.pages.render_page,
                           toc=toc,
                           chapter_content=get_chapter_content(chapter, toc), next=next, previous=previous)


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
        session['user'] = {"username": username}
        return seeother('/')


@app.route("/logout")
def log_out():
    if "user" in session:
        saml = session["user"].get("login_method", None) == "saml"
        session.pop("user", None)
        if True or saml:
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
                user = User(name=username, full_name=realname, email=email, hash_password=None, change_password_url=None)
                db_session.add(user)
                db_session.commit()

            session["user"] = {"username": user.username, "email": user.email, "login_method": "saml"}

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
    init_db()
    app.run(host='0.0.0.0', port=5000)
