# How to install
You will first need flask:
`pip3 install Flask`

Then install the *dependencies*, described in the `dependencies` file.

This application relies on INGInious, you can read the installation instructions
of INGInious here:

http://inginious.readthedocs.io/en/latest/install_doc/installation.html

More precisely, this application uses the simple-grader plugin. To install this plugin,
follow the instructions here:

 http://inginious.readthedocs.io/en/latest/install_doc/config_reference.html#simple-grader-plugin-webapp-lti

on the configuration of this plugin, set the `page_pattern` argument to `/tutorial`.

Finally, to have the site completely working, please add this inginious task to
the course you use for the syllabus:

https://github.com/OpenWeek/inginious-ucl-java-bac1/tree/master/M1Q7,

and name it `syllabus-test` (simply rename the directory of the task, nothing else is needed).
