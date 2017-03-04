from flask import Flask, render_template, request
import subprocess
import urllib
import json

import docutils

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
inginious_instance_hostname = "localhost"
inginious_instance_port = 8080


@app.route('/')
def hello_world():
    return render_template('hello.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port))


@app.route('/grade', methods=['POST'])
def grade():
    task_id = request.form["taskid"]
    inpt = request.form["input"]
    data = urllib.parse.urlencode({'taskid': task_id, 'input': inpt}).encode()
    # POST
    req = urllib.request.Request("http://%s:%d/tutorial" % (inginious_instance_hostname, inginious_instance_port),
                                 data=data)
    resp = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print(resp)
    p = subprocess.Popen(['rst2html5'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(bytes(resp["result"][1], encoding='utf-8'))
    out = p.communicate()
    return out


@app.route('/parserst', methods=['POST'])
def parse_rst():
    print(request.form)
    inpt = request.form["rst"]
    p = subprocess.Popen(['rst2html5'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(bytes(inpt, encoding='utf-8'))
    out = p.communicate()
    return out


if __name__ == '__main__':
    app.run()
