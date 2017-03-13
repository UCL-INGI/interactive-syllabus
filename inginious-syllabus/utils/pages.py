import os

from docutils.core import publish_string
from flask.helpers import get_root_path

default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'output_encoding': 'unicode',
    'input_encoding': 'unicode',
    'traceback': True,
    'halt_level': 5
}


def render_page(chapter, page):
    with open(os.path.join(get_root_path("inginious-syllabus"), "pages/%s/%s.rst" % (chapter, page)), "r") as f:
        return publish_string(f.read(), writer_name='html', settings_overrides=default_rst_opts)
