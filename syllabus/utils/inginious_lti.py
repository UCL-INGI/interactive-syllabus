from http.client import HTTPResponse

from lti import ToolConsumer
import syllabus.config as config
from urllib import request as urllib_request, parse
import re

lti_url_regex = re.compile("%s/@[0-9a-fA-F]+@/lti/task/?" % config.inginious_url)


def get_lti_url(user_id, task_id):
    consumer = ToolConsumer(
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret,
        launch_url='%s/lti/%s/%s' % (config.inginious_url, config.inginious_course_id, task_id),
        params={
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': "1.1",
            'resource_link_id': "syllabus_%s" % task_id,
            'user_id': user_id,
        }
    )

    d = consumer.generate_launch_data()
    data = parse.urlencode(d).encode()

    req = urllib_request.Request('%s/lti/%s/%s' % (config.inginious_url, config.inginious_course_id, task_id), data=data)
    resp = urllib_request.urlopen(req)

    task_url = resp.geturl()

    if not lti_url_regex.match(task_url):
        pass
        #raise Exception("INGInious returned the wrong url: %s vs %s" % (task_url, str(lti_url_regex)))
    return task_url


