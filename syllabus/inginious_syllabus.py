import os
from flask import Flask, render_template, request
import syllabus.utils.pages, syllabus.utils.directives
from syllabus.utils.pages import get_syllabus_toc, get_chapter_content
from docutils.core import publish_string
from syllabus.config import *
from docutils.parsers.rst import directives

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
directives.register_directive('inginious', syllabus.utils.directives.InginiousDirective)
directives.register_directive('table-of-contents', syllabus.utils.directives.ToCDirective)
directives.register_directive('author', syllabus.utils.directives.AuthorDirective)


@app.route('/')
@app.route('/index')
def index():
    toc = syllabus.get_toc()
    return render_template('rst_page.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port),
                           chapter="", page="index", render_rst=syllabus.utils.pages.render_page,
                           structure=get_syllabus_toc("pages"), list=list,
                           toc=toc,
                           chapter_content=None)


@app.route('/<chapter>')
def chapter_index(chapter):
    return render_web_page(chapter, None)


@app.route('/<chapter>/<page>')
@syllabus.utils.pages.sanitize_filenames
def get_page(chapter, page):
    return render_web_page(chapter, page)


def render_web_page(chapter, page):
    toc = syllabus.get_toc()
    if page is None:
        chapters = list(toc.keys())
        chapter_index = chapters.index(chapter)
        previous = None if chapter_index == 0 else chapters[chapter_index - 1]
        next = None if chapter_index == len(chapters) - 1 else chapters[chapter_index + 1]
    else:
        pages = list(toc[chapter]["content"].keys())
        page_index = pages.index(page)
        previous = None if page_index == 0 else pages[page_index - 1]
        next = None if page_index == len(pages) - 1 else pages[page_index + 1]
    return render_template('rst_page.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port),
                           chapter=chapter, page=page, render_rst=syllabus.utils.pages.render_page,
                           toc=toc,
                           chapter_content=get_chapter_content(chapter, toc), next=next, previous=previous)


@app.route('/parserst', methods=['POST'])
def parse_rst():
    inpt = request.form["rst"]
    out = publish_string(inpt, writer_name='html')
    return out


def main():
    app.run()
