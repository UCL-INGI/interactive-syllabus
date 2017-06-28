from syllabus.inginious_syllabus import main
from syllabus import get_root_path
import os

if __name__ == '__main__':
    path = os.path.join(get_root_path(), "pages")
    if not os.path.isdir(path):
        os.mkdir(path)
    main()
