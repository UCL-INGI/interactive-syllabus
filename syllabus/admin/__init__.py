from functools import wraps

import syllabus
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

from syllabus.models.user import User
from syllabus.utils.pages import permission_admin

admin_blueprint = Blueprint('admin', __name__,
                            template_folder='templates',
                            static_folder='static')

sidebar_elements = [{'id': 'users', 'name': 'Users'},
                    {'id': 'content_edition', 'name': 'Content Edition'}]

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
@permission_admin
@sidebar_page('users')
def users():
    try:
        return render_template('users.html', active_element=sidebar['active_element'],
                               sidebar_elements=sidebar['elements'], users=User.query.all())
    except TemplateNotFound:
        abort(404)


@admin_blueprint.route('/content_edition')
@permission_admin
@sidebar_page('content_edition')
def content_edition():
    try:
        TOC = syllabus.get_toc()
        return render_template('content_edition.html', active_element=sidebar['active_element'],
                               sidebar_elements=sidebar['elements'], TOC=TOC)
    except TemplateNotFound:
        abort(404)

