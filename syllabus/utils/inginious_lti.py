import json
from typing import Any, Dict
from urllib import parse

from lti1p3platform.ltiplatform import LTI1P3PlatformConfAbstract
from lti1p3platform.registration import Registration

from lti1p3platform.oidc_login import OIDCLoginAbstract
from lti1p3platform.message_launch import LTIAdvantageMessageLaunchAbstract

from flask import abort, redirect, render_template, jsonify, request, Blueprint, url_for

import syllabus

bp = Blueprint('lti', __name__, url_prefix='/lti')
platforms: Dict[str, 'LTIPlatformConf'] = {}

class LTIPlatformConf(LTI1P3PlatformConfAbstract):
    def init_platform_config(self, course):
        """
        register platform configuration
        """
        config = syllabus.get_config()
        assert course in config['courses'], f"Unknown course: {course}"
        lti_config = config['courses'][course]['inginious']['lti']
        registration = Registration() \
            .set_iss(lti_config['platform']['iss']) \
            .set_client_id(lti_config['platform']['client_id']) \
            .set_deployment_id(lti_config['platform']['deployment_id']) \
            .set_launch_url(lti_config['tool']['launch_url']) \
            .set_oidc_login_url(lti_config['tool']['oidc_login_url']) \
            .set_tool_key_set_url(lti_config['tool']['key_set_url']) \
            .set_platform_public_key(lti_config['platform']['public_key']) \
            .set_platform_private_key(lti_config['platform']['private_key'])

        self._registration = registration
        self.course = course
        platforms[course] = self

    def get_registration_by_params(self, **kwargs) -> Registration:
        return self._registration

    @classmethod
    def get_platform(cls, course):
        if course not in syllabus.get_config()['courses']:
            return abort(404)
        if course not in platforms:
            return LTIPlatformConf(course=course)
        return platforms[course]


class OIDCLogin(OIDCLoginAbstract):
    def set_lti_message_hint(self, **kwargs):
        self.hint = json.dumps(kwargs)

    def get_lti_message_hint(self):
        return self.hint

    def get_redirect(self, url):
        return redirect(url)


class LTI1p3MessageLaunch(LTIAdvantageMessageLaunchAbstract):
    deep_link = False

    def get_preflight_response(self) -> Dict[str, Any]:
        return request.form.copy() | request.args.copy()

    def render_launch_form(self, launch_data, **kwargs):
        return render_template("lti_tool_launch.html", **launch_data)

    def prepare_launch(self, preflight_response, **kwargs):
        message_hint = json.loads(parse.unquote_plus(preflight_response['lti_message_hint']))
        course_config = syllabus.get_config()['courses'][message_hint['course']]
        inginious_config = course_config['inginious']
        lti_config = inginious_config['lti']

        self.set_user_data(preflight_response['login_hint'], [])  # TODO(mp): Roles, see https://www.imsglobal.org/spec/lti/v1p3#role-vocabularies
        self.set_resource_link_claim("syllabus_{}_{}".format(message_hint['course'], message_hint['task_id']))
        launch_context = lti_config.get('launch_context', {})
        self.set_launch_context_claim(
            context_id=launch_context.get('id', message_hint['course']),
            context_label=launch_context.get('label', None),
            context_title=launch_context.get('title', course_config['title']),
            context_types=["http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering"]
        )
        launch_url = lti_config['tool']['launch_url']
        if not launch_url.endswith('/'):
            launch_url += '/'
        launch_url += message_hint['task_id']
        self.set_launch_url(launch_url)
        self.set_extra_claims({
            "https://purl.imsglobal.org/spec/lti/claim/tool_platform": {
                "guid": course_config['title'],
                "name": 'Interactive syllabus (%s)' % course_config['title'],
                "description": lti_config.get('platform_description', None),
                "url": lti_config.get('platform_url', None),
            },
        })

        if self.deep_link:
            self.set_dl(
                deep_link_return_url=url_for('lti.deep_link_return', course=message_hint['course'], _external=True),
                title='Interactive syllabus (%s - %s)' % (course_config['title'], message_hint['task_id']),
                accept_types={'html', 'ltiResourceLink'},
            )

def preflight_lti_1p3_launch(course, task_id, user_id):
    platform = LTIPlatformConf.get_platform(course)
    oidc_login = OIDCLogin(None, platform)
    oidc_login.set_lti_message_hint(course=course, task_id=task_id)
    launch_url = platform.get_registration().get_launch_url()
    if not launch_url.endswith('/'):
        launch_url += '/'
    launch_url += task_id
    oidc_login.set_launch_url(task_id)
    return oidc_login.prepare_preflight_url(user_id)

@bp.route('/jwks/<string:course>')
def get_jwks(course):
    return jsonify(LTIPlatformConf.get_platform(course).get_jwks())

@bp.route('/auth', methods=['GET', 'POST'])
def authorization():
    message_hint = json.loads(parse.unquote_plus(request.form.get('lti_message_hint', request.args.get('lti_message_hint'))))
    launch_request = LTI1p3MessageLaunch(None, LTIPlatformConf.get_platform(message_hint['course']))
    return launch_request.lti_launch()

@bp.route('/deep_link/<string:course>', methods=['POST'])
def deep_link_return(course):
    platform = LTIPlatformConf.get_platform(course)
    message = platform.tool_validate_and_decode(request.form.get('JWT', request.args.get('JWT')))
    return render_template('lti_deep_link_return.html', content_items=[c['html'] for c in message['https://purl.imsglobal.org/spec/lti-dl/claim/content_items']])


def get_lti_submission(course, user_id, task_id):
    import json
    from json import JSONDecodeError
    from urllib import request as urllib_request
    from urllib.error import HTTPError
    print('get_lti_submission', course, user_id, task_id)
    # TODO(mp): Find INGInious token/cookie from past launch attempts
    match = []
    if len(match) == 1:
        cookie = match[0]
        try:
            response = json.loads(urllib_request.urlopen('%s/lti/bestsubmission?session_id=%s' % (config['courses'][course]['inginious']['url'], cookie), timeout=5).read().decode("utf-8"))
        except (JSONDecodeError, HTTPError):
            response = {"status": "error"}
        if response["status"] == "success" and response["submission"] is not None:
            return response
    return None


def get_lti_data(course, user_id, task_id):
    parsed = parse.urlparse(preflight_lti_1p3_launch(course, task_id, user_id))
    query = parse.parse_qs(parsed.query)
    query['lti_message_hint'] = [parse.quote_plus(query['lti_message_hint'][0])]
    return {k: v[0] for k, v in query.items()}, parsed._replace(query='').geturl()
