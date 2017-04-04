import os
from collections import OrderedDict

import sys
from docutils.core import publish_string
from flask.helpers import get_root_path
from flask import render_template_string
from sphinx.websupport import WebSupport
from sphinx.application import Sphinx

import syllabus
from syllabus.config import *
import syllabus.utils.directives as directives
from syllabus.utils import rst


class MyWebSupport(WebSupport):
    def build(self):
        """Build the documentation. Places the data into the `outdir`
        directory. Use it like this::

            support = WebSupport(srcdir, builddir, search='xapian')
            support.build()

        This will read reStructured text files from `srcdir`. Then it will
        build the pickles and search index, placing them into `builddir`.
        It will also save node data to the database.
        """
        if not self.srcdir:
            raise RuntimeError('No srcdir associated with WebSupport object')
        app = Sphinx(self.srcdir, self.srcdir, self.outdir, self.doctreedir,
                     'websupport', status=self.status, warning=self.warning)
        app.builder.set_webinfo(self.staticdir, self.staticroot,
                                self.search, self.storage)
        app.add_directive('inginious', directives.InginiousDirective)
        app.add_directive('table-of-contents', directives.ToCDirective)

        self.storage.pre_build()
        app.build()
        self.storage.post_build()


# support = MyWebSupport(srcdir=os.path.join(get_root_path('inginious-syllabus'), 'pages'),
#                        builddir=os.path.join(get_root_path('inginious-syllabus'), 'pages-build'))
# support.build()

# print(support.get_document('index')['body'])

default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'output_encoding': 'unicode',
    'input_encoding': 'unicode',
    'traceback': True,
    'halt_level': 5
}


# TODO: define some explicit user-defined (YAML file ?) ordering of the chapters.
def get_syllabus_toc(wanted_root):
    """
    :param wanted_root: The directory from where the arborescence will start
    :return: An ordered dictionary containing the table of content of the syllabus.
    The chapters and pages inside chapters are ordered in lexicographical order
    """
    structure = OrderedDict()
    root_path = get_root_path("inginious-syllabus")
    split_root = wanted_root.split("/")
    node_name = split_root[len(split_root)-1]
    structure[node_name] = []
    for directory in sorted(os.listdir(os.path.join(root_path, wanted_root))):
        current_path = os.path.join(root_path,wanted_root, directory)
        if os.path.isdir(current_path):
            structure[node_name].append(get_syllabus_toc(os.path.join(wanted_root,directory)))
        else:
            structure[node_name].append(directory.replace('.rst', ''))
    print(structure)
    return structure


def render_page(chapter, page):
    root_path = get_root_path("syllabus")
    with open(os.path.join(root_path, "pages", chapter, "%s.rst" % page), "r") as f:
        return publish_string(render_template_string(f.read(), structure=get_syllabus_toc(),
                                                     hyperlink=rst.hyperlink, h=rst.h),
                              writer_name='html', settings_overrides=default_rst_opts)
