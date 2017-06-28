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
