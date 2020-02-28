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

import syllabus
from syllabus.utils.inginious_lti import get_lti_data, get_lti_submission
from syllabus.utils.pages import render_rst_str

from flask import session

def hyperlink(text, target):
    """
    Here are example of working targets:
    - `/mission1/page1` -> GET this path on the current hostname
    - `http://hostname:port/path`  -> GET this url
    :param text: the text to display to the user
    :param target: the hyperlink target (works like an a href)
    :return: The rst expression that shows an hyperlink going to the specified target
    """
    return "`%s <%s>`__" % (text, target)


def h(i, word):
    line = ''.join(['*' for x in word])
    return line


def bullet_list(l):
    return "- " + "\n- ".join(l)


def jinja_str(whatever):
    if whatever is None:
        return 'none'
    if type(whatever) is str:
        return '"{}"'.format(whatever)
    return str(whatever)


def get_html_inginious_lti(course_str, task_id):
    user = session.get("user", None)
    if user is None:
        return '<pre style="overflow: hidden; width: 100%; height: 520px">Please log in to see this exercise</pre>'
    else:
        data, launch_url = get_lti_data(course_str, user["email"], task_id)
        inputs_list = ['<input type="hidden" name="{0}" value="{1}"/>'.format(key, value) for key, value in data.items()]
        form_inputs = '\n'.join(inputs_list)
        return """
        <iframe name="myIframe{0}" frameborder="0" allowfullscreen"true" webkitallowfullscreen="true" mozallowfullscreen="true" scrolling="no"
            style="overflow: hidden; width: 100%; height: 520px" src=""></iframe>
        <form action="{1}"
              name="ltiLaunchForm"
              class="ltiLaunchForm"
              method="POST"
              encType="application/x-www-form-urlencoded"
              target="myIframe{0}">
              {2}
        <button class="inginious-submitter" type="submit">Launch the INGInious exercise</button>
        </form>
    """.format(task_id, launch_url, form_inputs)


def get_html_inginious_no_lti(task_id, prefilled_content, language):
    config = syllabus.get_config()
    html = """
        <div class="inginious-task" style="margin: 20px" data-language={0}">
            <div class="feedback-container" class="alert alert-success" style="padding: 10px;" hidden>
                <strong>Success!</strong> Indicates a successful or positive action.
            </div>
            <form method="post" action="{1}">
                <textarea style="width: 100%; height: 100%; height: 150px;" class="inginious-code" name="code">{2}</textarea><br/>
                <input type="text" name="taskid" class="taskid" value="{3}" hidden />
                <input type="text" name="input" class="to-submit" hidden />
            </form>
            <button class="btn btn-primary button-inginious-task" id="{3}" value="Submit">Soumettre</button>
        </div>
        """.format(language if language is not None else "text/x-python",
                   "/postinginious/" +  session["course"] if not config['same_origin_proxy'] else "inginious_sandbox_url",
                   prefilled_content,
                   task_id)
    return html

def get_html_inginious_print(course_str, task_id, prefilled_code, blank_lines):
    user = session.get("user", None)
    submission = get_lti_submission(course_str, user["email"], task_id) if user is not None else None
    if submission is not None:
        html = ""
        for item in submission['question_answer']:
            html += """
            <div>
            <div style="display: block; border: 1pc solid #000000; padding: 5px; border-radius: 5px;">
                <b>Question:</b>
                <br>
                {0}
                <br>
                <b>Answer {1}:</b>
                <br>
                <div style="font-family: Courier New, Courier">
                    {2}
                </div>
            </div>
            <br>
            """.format(render_rst_str(item['question']),
                       "(correct)" if item['success'] else "(incorrect)",
                       render_rst_str(item['answer']))
        return html
    else:
        if prefilled_code is not None:
            return """
            <pre>
                {0}
                {1}
            </pre>
            """.format(prefilled_code, '\n'*blank_lines)
    return """
    <pre>
    </pre>
    """


def get_inginious_html(course_str, task_id, language, prefilled_code, blank_lines, sandbox):
    if not session.get("print_mode", False):
        if sandbox:
            html_no_print = get_html_inginious_no_lti(task_id, prefilled_code, language)
        else:
            inginious_config = syllabus.get_config()['courses'][course_str]['inginious']
            if "lti" in inginious_config:
                html_no_print = get_html_inginious_lti(course_str, task_id)
            else:
                html_no_print = get_html_inginious_no_lti(task_id, prefilled_code, blank_lines)
        return html_no_print
    else:
        html_print = get_html_inginious_print(course_str, task_id, prefilled_code, blank_lines)
        return html_print
