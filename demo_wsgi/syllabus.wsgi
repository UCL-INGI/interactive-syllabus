import shutil
import os
import yaml
import syllabus
from syllabus.database import init_db, update_database

default_toc = \
    {
        "contribuer": {
            "title": "Contribuer au syllabus",
            "content": {
                "contribuer": {
                    "title": "Contribuer au contenu du syllabus"
                },
                "create_task": {
                    "title": "Créer une tâche INGInious"
                }
            }
        }
    }

# default pages directory location
path = os.path.join(syllabus.get_root_path(), "pages")
if syllabus.config.syllabus_pages_repo_origin is not None:
    pages.init_and_sync_repo()
if not os.path.isdir(path) and not os.path.isfile(path):
        shutil.copytree(os.path.join(syllabus.get_root_path(), "default", "pages"), path)
if not os.path.isfile(os.path.join(path, "toc.yaml")):
    with open(os.path.join(path, "toc.yaml"), "w+") as f:
        yaml.dump(default_toc, f)
init_db()
update_database()
from syllabus.inginious_syllabus import app as application
