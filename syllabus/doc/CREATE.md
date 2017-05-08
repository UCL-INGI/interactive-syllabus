# Create content for the syllabus
The syllabus is written in ReStructuredText. The pages of the syllabus are located in the `pages` directory. The syllabus structure is organized in chapter-page structure. Each directory in `pages` represents a chapter and each `.rst` file in a chapter represents a page in the chapter.

This syllabus offers different custom RST directives like the `inginious` directive and the `table-of-contents` directive.

#### The `inginious` directive
As this syllabus is directly correlated to INGInious, we offer a straightforward way to have a link between this syllabus and an INGInious instance.
Let's see this directly with an example :

```
--- interesting text about the theory of the syllabus ---

.. inginious:: task-name

    optional content
   
--- continue the theory here ---
```

The `inginious` directive will create a `textArea` whose content will be
submitted to the specified INGInious task. The optional content of the directive
permits to pre-fill the content of the `textArea` in order to create exercises with some 
pre-filled content in the `textArea`.

The `hostname:port` pair of the INGInious instance on which the content is submitted as well as the INGInious course id where the tasks
are located are specified in the `config.py` file. For the moment, the syllabus will assume that the INGInious tasks are
all one-question tasks and that the question id is `q1`.

An example of INGInious course working with the page 1 of this syllabus is available on this link
[this link](https://www.dropbox.com/sh/xz3r2ls9s9ebdhr/AAAWA_Qmu8F7iMDqvtNKDCDYa?dl=1)

#### The `table-of-contents` directive
There are different ways to move in the syllabus. The classical way is with a table of content in the first page of the syllabus. However, since chapter may have link between them, it may be usefull to list some reference inside a page.

##### The classical way
First, let assume that we want to make a classic ToC and we have a syllabus structured like this:

```
|- root
    |- chapter 1
        |- page1.rst
        |- page2.rst
    |- chapter 2
        |- page1.rst
        |- page2.rst
```
Then a option should be use with the directive, and this option must be the path to the root directory. So we should have something like

```
.. table-of-contents:: <path_to_root>

    optional redefining of page name
```
**Note** that the path is taken from the python module
By default, the shown name will be (assuming the entry link to the page page1.rst) page1. You can override this behaviour by adding a single line of the form
```
.. name: <Name that you want to be display>
```
at the first line of your page.

##### Link between chapter
If you want to make a list of reference to other pages of the syllabus, it can be done by using the ToC directive with no option. With the structure describe above, we can have something like
```
--- interesting text about the theory of the syllabus ---
References can be found here:

.. table-of-contents::

	Look at this page!|/chapter 1/page1
	<optional_rename>|<path_to_file>
	...
	<optional_rename>|<path_to_file>

--- continue the theory here ---
```
The optional renaming will overwrite the one in the `.rst` file. The path to the file should start from root, start with a `/` and drop the `.rst`.
