import json
import re
from json import JSONDecodeError
from urllib import request as urllib_request, parse
from urllib.error import URLError, HTTPError

from lti import ToolConsumer

import syllabus

lti_regex_match = re.compile('/@([0-9a-fA-F]+?)@/')


def get_lti_url(course, user_id, task_id):
    config = syllabus.get_config()
    inginious_config = config['courses'][course]['inginious']
    consumer = ToolConsumer(
        consumer_key=inginious_config['lti']['consumer_key'],
        consumer_secret=inginious_config['lti']['consumer_secret'],
        launch_url='%s/lti/%s/%s' % (inginious_config['url'], inginious_config['course_id'], task_id),
        params={
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': "1.1",
            'resource_link_id': "syllabus_{}_{}".format(course, task_id),
            'user_id': user_id,
        }
    )

    d = consumer.generate_launch_data()
    data = parse.urlencode(d).encode()

    req = urllib_request.Request('%s/lti/%s/%s' % (inginious_config['url'], inginious_config['course_id'], task_id), data=data)
    resp = urllib_request.urlopen(req)

    task_url = resp.geturl()

    lti_url_regex = re.compile("%s/@[0-9a-fA-F]+@/lti/task/?" % inginious_config['url'])
    if not lti_url_regex.match(task_url):
        pass
        #raise Exception("INGInious returned the wrong url: %s vs %s" % (task_url, str(lti_url_regex)))
    return task_url


def get_lti_submission(course, user_id, task_id):
    config = syllabus.get_config()
    try:
        lti_url = get_lti_url(course, user_id, task_id)
    except HTTPError:
        return None
    match = lti_regex_match.findall(lti_url)
    if len(match) == 1:
        cookie = match[0]
        try:
            response = json.loads(urllib_request.urlopen('%s/@%s@/lti/bestsubmission' % (config['courses'][course]['inginious']['url'], cookie), timeout=5).read().decode("utf-8"))
        except (JSONDecodeError, HTTPError):
            response = {"status": "error"}
        if response["status"] == "success" and response["submission"] is not None:
            return response
    return None


def get_lti_data(course, user_id, task_id):
    course_config = syllabus.get_config()['courses'][course]
    inginious_config = course_config['inginious']
    lti_config = inginious_config['lti']
    consumer = ToolConsumer(
        consumer_key=inginious_config['lti']['consumer_key'],
        consumer_secret=inginious_config['lti']['consumer_secret'],
        launch_url='%s/lti/%s/%s' % (inginious_config['url'], inginious_config['course_id'], task_id),
        params={
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': "1.1",
            'resource_link_id': "syllabus_%s" % task_id,
            'tool_consumer_instance_name': 'Interactive syllabus (%s)' % course_config['title'],
            'tool_consumer_instance_url': lti_config.get('tool_url', None),
            'tool_consumer_instance_description': lti_config.get('tool_description', None),
            'context_id': lti_config.get('tool_context_id', None),
            'context_label': lti_config.get('tool_context_label', None),
            'context_title': lti_config.get('tool_context_title', None),
            'user_id': user_id,
        }
    )

    d = consumer.generate_launch_data()
    return d, consumer.launch_url


