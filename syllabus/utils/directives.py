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
from urllib.error import URLError, HTTPError

from docutils.parsers.rst import Directive
from docutils import nodes
from docutils.parsers.rst.directives.body import CodeBlock
from docutils.statemachine import ViewList, StringList
from flask import session

import syllabus.utils.pages

from syllabus.config import *
from syllabus.utils.inginious_lti import get_lti_url
from syllabus.utils.toc import Chapter


class InginiousDirective(Directive):
    """
    required argument: the task id on which post the answer on INGInious
    optional argument 1: the language mode supported by CodeMirror
    optional argument 2: the number of blank lines to display in print mode
    directive content: the prefilled code in the text area
    """
    print = False
    has_content = True
    required_arguments = 1
    optional_arguments = 2
    html = """
    <div class="inginious-task" style="margin: 20px" data-language="{3}">
        <div class="feedback-container" class="alert alert-success" style="padding: 10px;" hidden>
            <strong>Success!</strong> Indicates a successful or positive action.
        </div>
        <form method="post" action="{0}">
            <textarea style="width:100%; height:150px;" class="inginious-code" name="code">{1}</textarea><br/>
            <input type="text" name="taskid" class="taskid" value="{2}" hidden/>
            <input type="text" name="input" class="to-submit" hidden/>
        </form>
        <button class="btn btn-primary button-inginious-task" id="{2}" value="Submit">Soumettre</button>
    </div>

    """

    def run(self):
        if not self.print:
            if not use_lti:
                par = nodes.raw('', self.html.format(inginious_course_url if not same_origin_proxy else "/postinginious",
                                                     '\n'.join(self.content),
                                                     self.arguments[0], self.arguments[1] if len(self.arguments) == 2 else "text/x-java"),
                                format='html')
            else:
                try:
                    user = session.get("user", None)
                    lti_url = get_lti_url(user.get("username", None) if user is not None else None, self.arguments[0])
                    par = nodes.raw('',
                                    '<iframe frameborder="0" onload="resizeIframe(this)" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true" scrolling="no"'
                                    ''
                                    ' style="overflow: hidden; width: 100%%; height: 520px" src="%s"></iframe>' % (
                                    lti_url), format='html')
                except (URLError, HTTPError) as e:
                    message = str(e.errno)
                    if "connection refused" in str(e.reason).lower():  # Handle connection refused
                        message = "impossible to connect to INGInious: connection refused"
                    elif type(e) is HTTPError:  # Handle HTTP errors from INGInious
                        if e.errno == 303:
                            message = "impossible to connect to INGInious: your account does not match an INGInious account"
                        elif e.errno == 500:
                            message = "impossible to connect to INGInious: INGInious internal error"

                    par = nodes.raw('',
                                    '<pre style="overflow: hidden; width: 100%%; height: 520px"> %s </pre>' % (
                                        message), format='html')

        else:
            n_blank_lines = int(self.arguments[2]) if len(self.arguments) == 3 else 0
            if self.content:
                sl = StringList(" "*n_blank_lines)
                self.content.append(sl)
                # par = nodes.literal_block('yaml',"%s%s" % ('\n'.join(self.content), "\n"*n_blank_lines), classes=["code", "yaml", "literal-block"])
                cb = CodeBlock(arguments=["yaml"], content=self.content, lineno=self.lineno,
                               block_text=self.block_text, content_offset=self.content_offset, name="code-block",
                               options=self.options, state=self.state, state_machine=self.state_machine)
                return cb.run()
            else:
                if n_blank_lines == 0:
                    n_blank_lines = 1
                par = nodes.raw('', """<pre>%s</pre>""" % ("\n"*n_blank_lines), format='html')
        return [par]


class ToCDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    html = """
    <div id="table-of-contents">
        <h2> Table des matières </h2>
    """

    def run(self):
        toc = syllabus.get_toc()
        if len(self.arguments) == 1:
            chapter = toc.get_chapter_from_path(self.arguments[0])
            self.html += "<h3> " + chapter.title + "</h3>\n"
            self.html += self.parse(toc, chapter)
        else:
            # for keys in toc.keys():
            #     self.html += "<h3> " + toc[keys]["title"] + "</h3>\n"
            #     self.html += self.parse(toc[keys]["content"], keys + "/")
            self.html += self.parse(toc)
        return [nodes.raw(' ', self.html, format='html')]

    def parse(self, toc, chapter=None):
        top_level = toc.get_top_level_content() if chapter is None else toc.get_direct_content_of(chapter)

        tmp_html = "<ul>\n"
        for content in top_level:
            tmp_html += '<li style="list-style-type: none;"><a href="/syllabus/' + content.request_path + '">' + content.title + '</a></li>\n'
            if type(content) is Chapter:
                tmp_html += self.parse(toc, content)
        tmp_html += "</ul>"
        return tmp_html


class AuthorDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0

    def run(self):
        html = '<div align=right><div style="display: inline-block;"><p><small> Auteur(s) : ' + self.content[0] + '</small></p>'
        html += '<hr style="margin-top: -5px;;" >\n'
        html += '</div></div>'
        return [nodes.raw(' ', html, format='html')]
