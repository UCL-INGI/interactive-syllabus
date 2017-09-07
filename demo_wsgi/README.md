# Vagrant for WSGI server example
This directory contains a Vagrant configuration that will setup an `httpd` wsgi server with the INGInious syllabus


## What it does
Basically, it :
* Disables `selinux`
* Installs all the needed dependencies for the interactive-syllabus, and `httpd`
* Installs the mod_wsgi module for httpd.
* Configures `httpd` to host syllabus on port 80 of the VM. **It does not need a particular hostname and answers to everybody.** 
* Tells `httpd` to set the `SYLLABUS_PAGES_PATH` environment variable by default to `/var/www/interavtive-syllabus/syllabus` which is the location where default `pages/` directory will be created. You can change this variable to put your pages in a different location.
* Installs the syllabus from the `master` branch, in the `/var/www/interactive-syllabus` directory of the VM.

