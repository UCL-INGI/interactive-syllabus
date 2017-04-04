import os
from flask import Flask, render_template, request
import syllabus.utils.pages, syllabus.utils.directives
from docutils.core import publish_string
from syllabus.config import *
from docutils.parsers.rst import directives

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
directives.register_directive('inginious', syllabus.utils.directives.InginiousDirective)
directives.register_directive('table-of-contents', syllabus.utils.directives.ToCDirective)

def hello_world():
    return render_template('hello.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port))


@app.route('/')
@app.route('/index')
def index():
    return render_template('hello_rst.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port),
                           chapter="", page="index", render_rst=syllabus.utils.pages.render_page)


@app.route('/<chapter>/<page>')
def get_page(chapter, page):
    return render_template('hello_rst.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port),
                           chapter=chapter, page=page, render_rst=syllabus.utils.pages.render_page)


@app.route('/parserst', methods=['POST'])
def parse_rst():
    inpt = request.form["rst"]
    out = publish_string(inpt, writer_name='html')
    return out


def main():
    app.run()
