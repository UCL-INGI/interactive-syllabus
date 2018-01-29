# Vagrant for WSGI server example
This directory contains a Vagrant configuration that will setup an `httpd` wsgi server with the INGInious syllabus


## What it does
Basically, it :
* Disables `selinux`
* Installs all the needed dependencies for the interactive-syllabus, and `httpd`
* Installs the mod_wsgi module for httpd.
* Configures `httpd` to host syllabus on port 80 of the VM. **It does not need a particular hostname and answers to everybody.** 
* Tells `httpd` to set the `SYLLABUS_PAGES_PATH` environment variable by default to `/var/www/interavtive-syllabus/syllabus` which is the location where a default `pages/` directory will be created to contain the pages of the syllabus. You can change this variable (in `/etc/httpd/conf/httpd.conf` in versions of httpd before 2.4 and early 2.4 subversions, or in the file set as you EnvironmentFile for versions of httpd that do not use the sysconfig file anymore) to put your pages in a different location.
* Installs the syllabus from the `master` branch, in the `/var/www/interactive-syllabus` directory of the VM.

## Configure the syllabus

You can set in `syllabus/config.py` the url of the INGInious course which has to be available via the Simple Grader plugin.

If the INGInious exercises do not work in the syllabus because of Cross Origin restrictions and you don't want to allow
CORS with your INGInious instance, you can put `same_origin_proxy` value to `True` in `syllabus/config.py` to avoid this
problem.use