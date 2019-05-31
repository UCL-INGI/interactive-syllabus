# Interactive Syllabus
The Interactive Syllabus allows you to write syllabus (either with [Sphinx](https://www.sphinx-doc.org/en/master/) or 
with the Python `docutils` rST) and insert automatically-graded exercises in it using 
[INGInious](https://inginious.org/?lang=en).


# How to install

You will first need to install the external dependancies for `xmlsec`. The installation procedure depends on your Linux 
distribution, go to [this page](https://github.com/mehcode/python-xmlsec#pre-install) and follow the instructions under the 
**Pre-Install** section. 


The Interactive Syllabus application relies on INGInious, you can read the installation instructions
of INGInious [here](http://inginious.readthedocs.io/en/latest/install_doc/installation.html).

In order to display INGInious exercises to students, the syllabus can either use LTI or the simple-grader INGInious
plugin. To install this plugin, follow the instructions 
[here](http://inginious.readthedocs.io/en/latest/install_doc/config_reference.html#simple-grader-plugin-webapp-lti).


Once you have a running INGInious instance, create an INGInious course that will contain the INGInious tasks for your
interactive syllabus (or download an INGInious course that contains the tasks you need, like 
[this one](https://github.com/UCL-INGI/CS1-Java)).

You can then install this application with pip3 (we currently support python3.6+), with the following command :

    pip3 install git+https://github.com/OpenWeek/interactive-syllabus

The syllabus will search for a special configuration file named `configuration.yaml` (an example can be found on this 
repository in `configuration_default.yaml`). This file contains the whole configuration of the syllabus. The application 
will search in your current working directory by default. If you want to put this file in another location, you can set
the `SYLLABUS_CONFIG_PATH` environment variable that points to the path to directory that contains `configuration.yaml`
file. This file allows you to define specific parameters for each of your courses 
(the INGInious instance, the INGInious course ID, ...).

If you want to have the `pages/` directory of your syllabus in a different location than the current working directory,
you can set the `SYLLABUS_PAGES_PATH` environment variable to the path that you want. 
Otherwise, you can set the `syllabus_pages_path` variable in your `configuration.yaml` file. 

You can now use this rST directive :

```
.. inginious:: task-id
    // pre-filled code (can be empty)
```
This will insert the INGInious task referred by `task-id` in the syllabus page.

To run a syllabus instance locally, run the `interactive-syllabus` command.

# WSGI

I you plan to use `WSGI`, execute the `syllabus.wsgi` script instead of the `syllabus-webapp` script located in the 
`demo_wsgi` directory.
