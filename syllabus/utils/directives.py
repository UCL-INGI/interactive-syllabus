from docutils.parsers.rst import Directive
from docutils import nodes

import syllabus.utils.pages

from syllabus.config import *

class InginiousDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    html = """
    <div id="feedback-container" class="alert alert-success" hidden>
        <strong>Success!</strong> Indicates a successful or positive action.
    </div>
    <form method="post" id="form1" action="http://{0}:{1}/{2}">
        <textarea style="width:100%; height:150px;" id="code" name="code"></textarea><br/>
        <input type="text" name="taskid" id="taskid" value="{3}" hidden/>
        <input type="text" name="input" id="to-submit" hidden/>
    </form>
    <button class="btn btn-primary button-inginious-task" id="b1" value="Submit">Submit</button>

    """

    def run(self):
        print(self.arguments[0])
        par = nodes.raw('', self.html.format(inginious_instance_hostname, inginious_instance_port,
                                             inginious_instance_course_id, self.arguments[0]), format='html')
        return [par]


class ToCDirective(Directive):
    required_arguments = 0
    optional_arguments = 0
    html = """
    <div id="table-of-contents">
        <h1> Table des matières! </h1>
        <ol type="I">
    """

    def run(self):
        toc = syllabus.utils.pages.get_syllabus_toc()
        for directory in toc:
            self.html += "\t\t<li>"+directory+"</li>\n"
            self.html += "\t\t<ol>\n"
            for file in toc[directory]:
                self.html += "\t\t\t<li><a href='"+directory+"/"+file+"'>"+file+"</a></li>\n"
            self.html += "\t\t</ol>\n"
        self.html += "\t</ol>\n</div>"
        return [nodes.raw(' ', self.html, format='html')]