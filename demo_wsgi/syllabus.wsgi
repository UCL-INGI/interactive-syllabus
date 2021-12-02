#!/bin/env python3

import shutil
import os
import yaml

# use it to set environment variables with WSGI outside the request context
# it is mostly useful if you want several instances of the syllabus having
# different values for these variables: you only need to duplicate this file
# and change these variables

ENV_VARS = {
               "SYLLABUS_CONFIG_PATH":  "/home/syllabus/interactive-syllabus",
#              "SYLLABUS_DATABASE_URI": "database_uri"
           }

for name, val in ENV_VARS.items():
    if val is not None:
        os.environ[name] = val

import syllabus
from syllabus.utils import pages
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
syllabus_config = syllabus.get_config()
for course in syllabus_config["courses"].keys():
    path = os.path.join(syllabus.get_pages_path(course))
    if not os.path.isdir(path) and not os.path.isfile(path):
            shutil.copytree(os.path.join(syllabus.get_root_path(), "default", "pages"), path)
    if 'git' in syllabus_config['courses'][course]['pages']:
        pages.init_and_sync_repo(course)

    if not os.path.isfile(os.path.join(path, "toc.yaml")):
        with open(os.path.join(path, "toc.yaml"), "w+") as f:
            yaml.dump(default_toc, f)
update_database()
init_db()
from syllabus.inginious_syllabus import app as application
