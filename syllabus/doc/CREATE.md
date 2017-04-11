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