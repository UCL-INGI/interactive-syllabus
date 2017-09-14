# How to install
You will first need flask:
`pip3 install Flask`

This application relies on INGInious, you can read the installation instructions
of INGInious here:

http://inginious.readthedocs.io/en/latest/install_doc/installation.html

More precisely, this application uses the simple-grader plugin. To install this plugin,
follow the instructions here:

 http://inginious.readthedocs.io/en/latest/install_doc/config_reference.html#simple-grader-plugin-webapp-lti

You can then install this application with pip3.
If you want to have the `pages/`directory of your syllabus in a different location than the current working directory, you can set the `SYLLABUS_PAGES_PATH` environment variable to the path that you want (also works if set `apache` (`SetEnv` directive) with `mod_wsgi`).

We currently support python3.5+.
