from docutils.parsers.rst import Directive
from docutils import nodes
import collections
import os

import syllabus.utils.pages

from syllabus.config import *


class InginiousDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    html = """
    <div class="inginious-task" style="margin: 20px">
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
                                             self.arguments[0]), format='html')
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
        if len(self.arguments) == 0:
            tmp = "<ol>\n"
            for line in self.content:
                splitted = line.split("|")
                if len(splitted) == 2:
                    tmp += '<li style="list-style-type: none;"><a href=' + splitted[1] + '>' + splitted[0] + '</a></li>\n'
                else:
                    tmp += '<li style="list-style-type: none;"><a href=' + line + '>' + self.getName("pages/"+splitted[0]) + '</a></li>\n'
            tmp += "</ol>"
            return [nodes.raw(' ', tmp, format='html')]

        toc = syllabus.utils.pages.get_syllabus_toc(self.arguments[0])
        self.html += self.parse(toc[self.arguments[0]], "")
        self.html += "</div>"
        return [nodes.raw(' ', self.html, format='html')]

    def parse(self, dictio, pathTo):

        if pathTo == "":
            html = "<ul>"
        else:
            split = pathTo.split("/")
            html = "<h" + str(len(split)+1) + ">" + split[len(split)-1] + "</h" + str(len(split)+1) + ">\n<ul>"
        for elem in dictio:
            if isinstance(elem, collections.OrderedDict):
                for k in elem:
                    key = k
                html += self.parse(elem[key], pathTo+"/"+key)
            else:
                directory = os.path.join(os.getcwd(), "pages")
                for s in pathTo.split("/"):
                    directory = os.path.join(directory, s)
                directory = os.path.join(directory, elem)
                name = self.getName(directory)
                html += "<li style=\"list-style-type: none;\"><a href='" + pathTo + "/" + elem + "'>" + name + "</a>"
        html += "</ul>"
        return html

    def getName(self, path):
        with open(path+".rst", 'r') as f:
            first = f.readline()
            if first[:8] == ".. name:":
                return str(first[8:])
            else:
                tab = path.split("/")
                return tab[len(tab)-1]

    def getContent(self, content):
        return "Hello"
