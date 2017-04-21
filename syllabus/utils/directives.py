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
    """
    This is a class for the table of contents directive. This directive support multiple format for different 
    usage:

        1) If there is no option to the directive, the content of the directive must follow the following schema:
            
            - Line of the content represent 1 entry in the ToC
            - The line must have the following format : <Text that will be display>|<path to the rst page>

        2) If there is an option to the directive, this option must be the directory from where the ToC should
            start. There is 2 ways to use the directive with an option

            - By default, the entry in the ToC will be name by taking the name of the file and removing the ".rst" suffix.
            - To change this behavior, a line must be inserted at the beginning of the file. This should be a rst comment of the form : ".. name: The text that will be display". In this case, the entry will be "The text that will be display"
        
            
    """
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
                tmp += '<li style="list-style-type: none;"><a href=' + splitted[1] + '>' + splitted[0] + '</a></li>\n'
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
                directory = os.path.join(os.getcwd(),"pages")
                for s in pathTo.split("/"):
                    directory = os.path.join(directory,s)
                directory = os.path.join(directory,elem)
                name = self.getName(directory)
                html += "<li style=\"list-style-type: none;\"><a href='" + pathTo + "/" + elem + "'>" + name + "</a>"
        html += "</ul>"
        return html

    def getName(self, path):
        with open(path+".rst",'r') as f:
            first = f.readline()
            if first[:8] == ".. name:":
                return str(first[8:])
            else:
                tab = path.split("/")
                return tab[len(tab)-1]


    def getContent(self, content):
        return "Hello"
