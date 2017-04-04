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
