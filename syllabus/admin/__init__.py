import shutil
from functools import wraps

import os

import re
import yaml

from syllabus.database import db_session
from syllabus.models.params import Params
from syllabus.utils.feedbacks import *
from syllabus.utils.toc import TableOfContent, ContentNotFoundError, Page, Chapter
from syllabus.utils.yaml_ordered_dict import OrderedDictYAMLLoader

import syllabus
from flask import Blueprint, render_template, abort, request, session
from jinja2 import TemplateNotFound

from syllabus.models.user import User
from syllabus.utils.pages import permission_admin, seeother

admin_blueprint = Blueprint('admin', __name__,
                            template_folder='templates',
                            static_folder='static')

sidebar_elements = [{'id': 'users', 'name': 'Users', 'icon': 'users'}] + \
                    [{'id': 'content_edition/' + course, 'name': 'Content Edition ' + course, 'icon': 'edit'} for course in syllabus.get_courses()] + \
                    [{'id': 'toc_edition/' + course, 'name': 'ToC Edition ' + course, 'icon': 'list'} for course in syllabus.get_courses()] + \
                    [{'id': 'config_edition', 'name': 'Configuration Edition', 'icon': 'cog'}]

sidebar = {'active_element': 'users', 'elements': sidebar_elements}


def sidebar_page(element):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            sidebar['active_element'] = element
            return f(*args, **kwargs)
        return wrapper
    return decorator


@admin_blueprint.route('/users', methods=['GET', 'POST'])
@permission_admin
@sidebar_page('users')
def users():
    if request.method == 'POST':
        inpt = request.form
        if inpt["action"] == "change_right":
            user = User.query.filter(User.username == inpt["username"]).first()
            if user.username == session["user"]["username"]:
                return seeother(request.path)
            user.right = "admin" if "admin" in inpt and inpt["admin"] == "on" else None
            db_session.commit()
            return seeother(request.path, SuccessFeedback("The rights of %s have been successfully edited" % user.username))
        return seeother(request.path)
    try:
        return render_template('users.html', active_element=sidebar['active_element'],
                               sidebar_elements=sidebar['elements'], users=User.query.all(),
                               feedback=pop_feeback(session))
    except TemplateNotFound:
        abort(404)


@admin_blueprint.route('/content_edition/<string:course>', methods=['GET', 'POST'])
@permission_admin
@sidebar_page('content_edition')
def content_edition(course):
    if not course in syllabus.get_config()["courses"].keys():
        abort(404)
    TOC = syllabus.get_toc(course)
    if TOC.ignored and not has_feedback(session):
        set_feedback(session, Feedback(feedback_type="warning", message="The following contents have not been found :\n"
                                                                        + "<pre>"
                                                                        + "\n".join(TOC.ignored)
                                                                        + "</pre>"))
    if request.method == "POST":
        inpt = request.form
        if inpt["action"] == "delete_content":
            return delete_content(course, inpt, TOC)
        containing_chapter = None
        try:
            if inpt["containing-chapter"] != "":
                containing_chapter = TOC.get_chapter_from_path(inpt["containing-chapter"])

        except ContentNotFoundError:
            set_feedback(session, Feedback(feedback_type="error", message="The containing chapter for this page "
                                                                          "does not exist"))
            return seeother(request.path)

        # sanity checks on the filename: refuse empty filenames of filenames with spaces
        if len(inpt["name"]) == 0 or len(re.sub(r'\s+', '', inpt["name"])) != len(inpt["name"]):
            set_feedback(session, Feedback(feedback_type="error", message='The file name cannot be empty or contain spaces.'))
            return seeother(request.path)

        if os.sep in inpt["name"]:
            set_feedback(session, Feedback(feedback_type="error", message='The file name cannot contain the "%s" forbidden character.' % os.sep))
            return seeother(request.path)

        pages_path = syllabus.get_pages_path()
        content_path = os.path.join(containing_chapter.path, inpt["name"]) if containing_chapter is not None else inpt["name"]
        path = os.path.join(pages_path, content_path)

        # ensure that we do not create a page at the top level
        if containing_chapter is None and inpt["action"] == "create_page":
            set_feedback(session, Feedback(feedback_type="error", message="Pages cannot be at the top level of the "
                                                                          "syllabus."))
            return seeother(request.path)

        # check that there is no chapter with the same title in the containing chapter
        if containing_chapter is None:
            for content in TOC.get_top_level_content():
                if content.title == inpt["title"]:
                    set_feedback(session, Feedback(feedback_type="error", message="There is already a top level "
                                                                                  "chapter with this title."))
                    return seeother(request.path)
        else:
            for content in TOC.get_direct_content_of(containing_chapter):
                if content.title == inpt["title"]:
                    set_feedback(session, Feedback(feedback_type="error", message="There is already a chapter/page "
                                                                                  "with this title in this chapter."))
                    return seeother(request.path)

        if inpt["action"] == "create_page":

            # add the extension to the page filename
            content_path += ".rst"
            path += ".rst"

            # when file/directory already exists
            if os.path.isdir(path) or os.path.isfile(path):
                set_feedback(session, Feedback(feedback_type="error", message="A file or directory with this name "
                                                                              "already exists."))
                return seeother(request.path)

            # create a new page
            open(path, "w").close()
            page = Page(path=content_path, title=inpt["title"], pages_path=syllabus.get_pages_path(course))
            TOC.add_content_in_toc(page)
        elif inpt["action"] == "create_chapter":
            # creating a new chapter
            try:
                os.mkdir(path)
            except FileExistsError:
                set_feedback(session, Feedback(feedback_type="error", message="A file or directory with this name "
                                                                              "already exists."))
                return seeother(request.path)
            chapter = Chapter(path=content_path, title=inpt["title"], pages_path=syllabus.get_pages_path(course))
            TOC.add_content_in_toc(chapter)

        # dump the TOC and reload it
        syllabus.save_toc(course, TOC)
        syllabus.get_toc(course, force=True)
        return seeother(request.path)
    try:
        return render_template('content_edition.html', active_element=sidebar['active_element'], course_str=course,
                               sidebar_elements=sidebar['elements'], TOC=TOC, feedback=pop_feeback(session))
    except TemplateNotFound:
        abort(404)


def delete_content(course, inpt, TOC):
    pages_path = syllabus.get_pages_path(course)
    content_path = inpt["content-path"]
    path = os.path.join(pages_path, content_path)

    content_to_delete = TOC.get_content_from_path(content_path)
    TOC.remove_content_from_toc(content_to_delete)

    # dump the TOC and reload it
    syllabus.save_toc(course, TOC)
    syllabus.get_toc(course, force=True)

    # remove the files if asked
    if inpt.get("delete-files", None) == "on":
        if type(content_to_delete) is Chapter:
            # delete a chapter
            shutil.rmtree(os.path.join(path))
        else:
            # delete a page
            os.remove(path)

    set_feedback(session, Feedback(feedback_type="success", message="The content has been successfully deleted"))
    return seeother(request.path)


@admin_blueprint.route('/toc_edition/<string:course>', methods=['GET', 'POST'])
@permission_admin
@sidebar_page('toc_edition')
def toc_edition(course):
    if not course in syllabus.get_config()["courses"].keys():
        abort(404)
    toc = syllabus.get_toc(course)
    if toc.ignored and not has_feedback(session):
        set_feedback(session, Feedback(feedback_type="warning", message="The following contents have not been found :\n"
                                                                        + "<pre>"
                                                                        + "\n".join(toc.ignored)
                                                                        + "</pre>"))
    if request.method == "POST":
        inpt = request.form
        if "new_content" in inpt:
            try:
                # check YAML validity
                toc_dict = yaml.load(inpt["new_content"], OrderedDictYAMLLoader)
                if not TableOfContent.is_toc_dict_valid(syllabus.get_pages_path(course), toc_dict):
                    set_feedback(session, Feedback(feedback_type="error", message="The submitted table of contents "
                                                                                  "is not consistent with the files "
                                                                                  "located in the pages directory."))
                    return seeother(request.path)
            except yaml.YAMLError:
                set_feedback(session, Feedback(feedback_type="error", message="The submitted table of contents is not "
                                                                              "written in valid YAML."))
                return seeother(request.path)
            # the YAML is valid, write it in the ToC
            with open(os.path.join(syllabus.get_pages_path(course), "toc.yaml"), "w") as f:
                f.write(inpt["new_content"])
            syllabus.get_toc(course, force=True)
        set_feedback(session, Feedback(feedback_type="success", message="The table of contents has been modified "
                                                                        "successfully !"))
        return seeother(request.path)
    else:
        with open(os.path.join(syllabus.get_pages_path(course), "toc.yaml"), "r") as f:
            try:
                return render_template('edit_table_of_content.html', active_element=sidebar['active_element'],
                                       sidebar_elements=sidebar['elements'], content=f.read(),
                                       feedback=pop_feeback(session))
            except TemplateNotFound:
                abort(404)


@admin_blueprint.route('/config_edition', methods=['GET', 'POST'])
@permission_admin
@sidebar_page('config_edition')
def config_edition():
    if request.method == "POST":
        inpt = request.form
        if "new_config" in inpt:
            try:
                # check YAML validity
                config = yaml.load(inpt["new_config"])
                # TODO: check that the configuration has the appropriate fields
                # update the config
                old_config = syllabus.get_config()
                syllabus.set_config(inpt["new_config"])
                # sync the git repo if it has changed
                try:
                    courses = set(list(old_config["courses"].keys()) + list(config["courses"].keys()))
                    for course in courses:
                        old_pages_config = old_config["courses"].get(course, {}).get("pages", {})
                        pages_config = config["courses"].get(course, {}).get("pages", {})
                        if ("git" not in old_pages_config and "git" in pages_config) or old_pages_config["git"] != pages_config["git"]:
                            syllabus.utils.pages.init_and_sync_repo(course, force_sync=True)
                except KeyError as e:
                    pass
                except AttributeError:
                    return seeother(request.path, Feedback(feedback_type="error", message="The git repository has "
                                                                                            "failed to synchronize. "
                                                                                            "Please check your "
                                                                                            "configuration."))
                return seeother(request.path, Feedback(feedback_type="success", message="The table of contents has been"
                                                                                        " modified successfully !"))
            except yaml.YAMLError:
                return seeother(request.path, feedback=Feedback(feedback_type="error",
                                                                message="The submitted configuration is not "
                                                                        "written in valid YAML."))
    else:
        params = Params.query.one()
        config = syllabus.get_config()
        hook_paths = [("/update_pages/{}/{}".format(params.git_hook_url, course)) if "git" in config["courses"][course]["pages"] and params.git_hook_url is not None else None for course in syllabus.get_courses()]
        try:
            with open(syllabus.get_config_path(), 'r') as f:
                return render_template('edit_configuration.html', active_element=sidebar['active_element'],
                                       sidebar_elements=sidebar['elements'], config=f.read(),
                                       hook_paths=hook_paths,
                                       feedback=pop_feeback(session))
        except TemplateNotFound:
            abort(404)
