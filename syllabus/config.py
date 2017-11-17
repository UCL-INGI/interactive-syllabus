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


inginious_url = "http://localhost:8080"

inginious_course_id = "tutorial"

inginious_course_url = "%s/%s" % (inginious_url, inginious_course_id)

# indicates the location where the pages directory is located. It has a lower priority than the SYLLABUS_PAGES_PATH
# environment variable. If none of these is set, the path will be considered as in the current working directory.
syllabus_pages_path = None

# if True, the INGInious POST requests will be sent to this server instead of the real
# INGINious instance. This server will then do the request itself to the INGInious instance,
# to avoid same origin policy problem (when the INGInious instance does not allow the use of CORS)
same_origin_proxy = True

### LTI RELATED CONFIG ###

use_lti = True

consumer_secret = 'my_super_key'

consumer_key = 'syllabus'
