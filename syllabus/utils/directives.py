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

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.body import CodeBlock
from docutils.statemachine import StringList
from flask import session

import syllabus.utils.pages
from syllabus.utils.inginious_lti import get_lti_url, get_lti_data
from syllabus.utils.toc import Chapter


class InginiousDirective(Directive):
    """
    required argument: the task id on which post the answer on INGInious
    optional argument 1: the language mode supported by CodeMirror
    optional argument 2: the number of blank lines to display in print mode
    directive content: the prefilled code in the text area

    The directive will display the content in print mode if the "print" attribute is set to True in the session.
    """
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

    def get_html_content(self, use_lti):
        if not session.get("print", False):
            if not use_lti:
                inginious_config = syllabus.get_config()['inginious']
                inginious_course_url = "%s/%s" % (inginious_config['url'], inginious_config['course_id'])
                same_origin_proxy = inginious_config['same_origin_proxy']
                par = nodes.raw('', self.html.format(inginious_course_url if not same_origin_proxy else "/postinginious",
                                                     '\n'.join(self.content),
                                                     self.arguments[0], self.arguments[1] if len(self.arguments) == 2 else "text/x-java"),
                                format='html')
            else:
                user = session.get("user", None)
                if user is not None:
                    data, launch_url = get_lti_data(user.get("username", None) if user is not None else None, self.arguments[0])
                    form_inputs = '\n'.join(['<input type="hidden" name="%s" value="%s"/>' % (key, value) for key, value in data.items()])
                    par = nodes.raw('',
                                    '<iframe name="myIframe%d" frameborder="0" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true" scrolling="no"'
                                    ''
                                    ' style="overflow: hidden; width: 100%%; height: 520px" src=""></iframe>'
                                    """
                                    <form action="%s"
                                          name="ltiLaunchForm"
                                          class="ltiLaunchForm"
                                          method="POST"
                                          encType="application/x-www-form-urlencoded"
                                          target="myIframe%s">
                                      %s
                                      <button class="inginious-submitter" type="submit">Launch the INGInious exercise</button>
                                    </form>
                                    """ % (self.arguments[0], launch_url, self.arguments[0], form_inputs),

                                    format='html')
                else:
                    par = nodes.raw('',
                                    '<pre style="overflow: hidden; width: 100%%; height: 520px"> Please log in to see this exercise </pre>',
                                    format='html')

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

    def run(self):
        return self.get_html_content("lti" in syllabus.get_config()["inginious"])


class InginiousSandboxDirective(InginiousDirective):
    def run(self):
        return self.get_html_content(False)


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
