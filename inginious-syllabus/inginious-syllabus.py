from flask import Flask, render_template, request
import utils.pages, utils.directives
from docutils.core import publish_string
from docutils.parsers.rst import directives

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
inginious_instance_hostname = "localhost"
inginious_instance_port = 8080
# directives.register_directive('inginious', utils.directives.InginiousDirective)


@app.route('/')
def hello_world():
    return render_template('hello.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port))


@app.route('/rst_version')
def hello_world_rst():
    return render_template('hello_rst.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port),
                           chapter="mission1", page="page1", render_rst=utils.pages.render_page)


@app.route('/parserst', methods=['POST'])
def parse_rst():
    inpt = request.form["rst"]
    out = publish_string(inpt, writer_name='html')
    return out


if __name__ == '__main__':
    app.run()
