from functools import wraps

import os

import yaml

from syllabus.utils.feedbacks import *
from syllabus.utils.toc import TableOfContent
from syllabus.utils.yaml_ordered_dict import OrderedDictYAMLLoader

import syllabus
from flask import Blueprint, render_template, abort, request, session
from jinja2 import TemplateNotFound

from syllabus.models.user import User
from syllabus.utils.pages import permission_admin, seeother

admin_blueprint = Blueprint('admin', __name__,
                            template_folder='templates',
                            static_folder='static')

sidebar_elements = [{'id': 'users', 'name': 'Users'},
                    {'id': 'content_edition', 'name': 'Content Edition'},
                    {'id': 'toc_edition', 'name': 'ToC Edition'}]

sidebar = {'active_element': 'users', 'elements': sidebar_elements}


def sidebar_page(element):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            sidebar['active_element'] = element
            return f(*args, **kwargs)
        return wrapper
    return decorator


@admin_blueprint.route('/users')
#@permission_admin
@sidebar_page('users')
def users():
    try:
        return render_template('users.html', active_element=sidebar['active_element'],
                               sidebar_elements=sidebar['elements'], users=User.query.all())
    except TemplateNotFound:
        abort(404)


@admin_blueprint.route('/content_edition')
#@permission_admin
@sidebar_page('content_edition')
def content_edition():
    try:
        TOC = syllabus.get_toc()
        return render_template('content_edition.html', active_element=sidebar['active_element'],
                               sidebar_elements=sidebar['elements'], TOC=TOC)
    except TemplateNotFound:
        abort(404)


@admin_blueprint.route('/toc_edition', methods=['GET', 'POST'])
#@permission_admin
@sidebar_page('toc_edition')
def toc_edition():
    if request.method == "POST":
        inpt = request.form
        if "new_content" in inpt:
            try:
                # check YAML validity
                toc_dict = yaml.load(inpt["new_content"], OrderedDictYAMLLoader)
                if not TableOfContent.is_toc_dict_valid(toc_dict):
                    set_feedback(session, Feedback(feedback_type="error", message="The submitted table of contents "
                                                                                  "is not consistent with the files "
                                                                                  "located in the pages directory."))
                    return seeother(request.path)
            except yaml.YAMLError:
                set_feedback(session, Feedback(feedback_type="error", message="The submitted table of contents is not "
                                                                              "written in valid YAML."))
                return seeother(request.path)
            # the YAML is valid, write it in the ToC
            with open(os.path.join(syllabus.get_pages_path(), "toc.yaml"), "w") as f:
                f.write(inpt["new_content"])
            syllabus.get_toc(force=True)
        set_feedback(session, Feedback(feedback_type="success", message="The table of contents has been modified "
                                                                        "successfully !"))
        return seeother(request.path)
    else:
        with open(os.path.join(syllabus.get_pages_path(), "toc.yaml"), "r") as f:
            try:
                return render_template('edit_table_of_content.html', active_element=sidebar['active_element'],
                                       sidebar_elements=sidebar['elements'], content=f.read(),
                                       feedback=pop_feeback(session))
            except TemplateNotFound:
                abort(404)
