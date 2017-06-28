from docutils.parsers.rst import Directive
from docutils import nodes

import syllabus.utils.pages

from syllabus.config import *


class InginiousDirective(Directive):
    """
    required argument: the task id on which post the answer on INGInious
    optional argument: the language mode supported by CodeMirror
    directive content: the prefilled code in the text area
    """
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    html = """
    <div class="inginious-task" style="margin: 20px" data-language="{5}">
        <div class="feedback-container" class="alert alert-success" style="padding: 10px;" hidden>
            <strong>Success!</strong> Indicates a successful or positive action.
        </div>
        <form method="post" action="http://{0}:{1}/{2}">
            <textarea style="width:100%; height:150px;" class="inginious-code" name="code">{3}</textarea><br/>
            <input type="text" name="taskid" class="taskid" value="{4}" hidden/>
            <input type="text" name="input" class="to-submit" hidden/>
        </form>
        <button class="btn btn-primary button-inginious-task" id="{4}" value="Submit">Submit</button>
    </div>

    """

    def run(self):
        par = nodes.raw('', self.html.format(inginious_instance_hostname, inginious_instance_port,
                                             inginious_instance_course_id, '\n'.join(self.content),
                                             self.arguments[0], self.arguments[1] if len(self.arguments) == 2 else "text/x-java"),
                        format='html')
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
            self.html += "<h3> " + toc[self.arguments[0]]["title"] + "</h3>\n"
            toc = toc[self.arguments[0]]["content"]
            self.html += self.parse(toc, self.arguments[0] + "/")
        else:
            for keys in toc.keys():
                self.html += "<h3> " + toc[keys]["title"] + "</h3>\n"
                self.html += self.parse(toc[keys]["content"], keys + "/")
        return [nodes.raw(' ', self.html, format='html')]

    def parse(self, dictio, pathTo):
        tmp_html = "<ul>\n"
        for key in dictio:
            tmp_html += '<li style="list-style-type: none;"><a href=' + pathTo +key + '>' + dictio[key]["title"] + '</a></li>\n'
            if "content" in dictio[key]:
                tmp_html += self.parse(dictio[key]["content"],pathTo+key+"/")
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
