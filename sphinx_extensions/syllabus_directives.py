from syllabus.utils.directives import *


def setup(app):
    app.add_directive('inginious', InginiousDirective)
    app.add_directive('inginious-sandbox', InginiousSandboxDirective)
    app.add_directive('table-of-contents', ToCDirective)
    app.add_directive('author', AuthorDirective)
    app.add_directive('teacher', TeacherDirective)
    app.add_directive('framed', FramedDirective)
    app.add_directive('print', PrintOnlyDirective)
