from docutils.parsers.rst import Directive
from inginious-syllabus
from docutils import nodes


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
        par = nodes.raw('', self.html.format(self.arguments[0]), format='html')
        return [par]
