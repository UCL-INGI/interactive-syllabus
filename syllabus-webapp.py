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



from syllabus import get_root_path
import os

if __name__ == '__main__':
    path = os.path.join(get_root_path(), "pages")
    if not os.path.isdir(path):
        chapter_index = """
{{ chapter_desc }}

.. table-of-contents:: {{ chapter_name }}
"""
        default_index = """
==================
Default index page
==================

--------------------------------------------------------------
This is the auto-generated index page for the syllabus webapp.
--------------------------------------------------------------
"""
        os.mkdir(path)
        with open(os.path.join(path, "chapter_index.rst"), "w+") as f:
            f.write(chapter_index)
        with open(os.path.join(path, "toc.yaml"), "w+") as f:
            pass
        with open(os.path.join(path, "index.rst"), "w+") as f:
            f.write(default_index)
    from syllabus.inginious_syllabus import main
    main()
