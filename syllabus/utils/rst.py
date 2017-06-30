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
