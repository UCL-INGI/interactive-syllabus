# How to install
You will first need flask:
`pip3 install Flask`

This application relies on INGInious, you can read the installation instructions
of INGInious here:

http://inginious.readthedocs.io/en/latest/install_doc/installation.html

More precisely, this application uses the simple-grader plugin. To install this plugin,
follow the instructions here:

 http://inginious.readthedocs.io/en/latest/install_doc/config_reference.html#simple-grader-plugin-webapp-lti


Once you have a running INGInious instance with the Simple Grader plugin activated, create an INGInious course that will contain the INGInious tasks for your interactive syllabus (or download an INGInious course that contains the tasks you need, like this one) and set it as the course that will be exposed via the Simple Grader plugin.

You can then install this application with pip3 (we currently support python3.5+).
If you want to have the `pages/`directory of your syllabus in a different location than the current working directory, you can set the `SYLLABUS_PAGES_PATH` WSGI environment variable to the path that you want if you use WSGI. Otherwise, you can set the `syllabus_pages_path` variable in `syllabus/config.py`.

Once you have installed the syllabus and one the INGInious course that will contain the tasks for the syllabus is correctly added in INGInious, set the `inginious_course_url` variable in `syllabus/config.py` to the url of your INGInious course exposed via the Simple Grader plugin (i.e. inginious instance hostname hostname + the path you defined in the `page_pattern` field in the configuration of the INGInious Simple Grader plugin).

You can now use this rST directive :

```
.. inginious:: task-id
    // pre-filled code (can be empty)
```
This will create a CodeMirror Text Area with a button to POST its content as the input of the task `task-id` of the course you exposed via the Simple Grader INGInious plugin, in order to grade the content and thus have a real-time feedback about the code written by the user of the syllabus.

# WSGI

I you plan to use `WSGI`, replace the `syllabus-webapp` script by the `syllabus.wsgi` script located in the `demo_wsgi` directory.
