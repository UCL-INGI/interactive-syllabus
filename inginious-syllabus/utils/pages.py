import os

from docutils.core import publish_string
from flask.helpers import get_root_path
from sphinx.websupport import WebSupport
from sphinx.application import Sphinx
import utils.directives as directives




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

        self.storage.pre_build()
        app.build()
        self.storage.post_build()


support = MyWebSupport(srcdir=os.path.join(get_root_path('inginious-syllabus'), 'pages'),
                       builddir=os.path.join(get_root_path('inginious-syllabus'), 'pages-build'))
support.build()

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


def render_page(chapter, page):
    with open(os.path.join(get_root_path("inginious-syllabus"), "pages/%s/%s.rst" % (chapter, page)), "r") as f:
        return publish_string(f.read(), writer_name='html', settings_overrides=default_rst_opts)
