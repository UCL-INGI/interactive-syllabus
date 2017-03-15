from docutils.parsers.rst import Directive
from docutils import nodes


class InginiousDirective(Directive):
    required_arguments = 0
    optional_arguments = 0
    html = """
    <div id="feedback-container" class="alert alert-success" hidden>
        <strong>Success!</strong> Indicates a successful or positive action.
    </div>
    <form method="post" id="form1" action="http://localhost:8080/tutorial">
        <textarea style="width:100%; height:150px;" id="code" name="code"></textarea><br/>
        <input type="text" name="taskid" id="taskid" value="syllabus-test" hidden/>
        <input type="text" name="input" id="to-submit" hidden/>
    </form>
    <button class="btn btn-primary" id="b1" value="Submit">Submit</button>

    """

    def run(self):
        par = nodes.raw('', self.html, format='html')
        return [par]
