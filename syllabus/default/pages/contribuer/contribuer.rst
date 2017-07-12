.. Cette page est publiée sous la license Creative Commons BY-SA (https://creativecommons.org/licenses/by-sa/3.0/fr/)

.. author::

    François Michel

==============================
Contribuer au contenu syllabus
==============================

Le contenu du syllabus est subdivisé en **chapitres**, chaque chapitre contenant une ou plusieurs **pages** écrites en ``rST``.
La page web que vous lisez actuellement est d'ailleurs la première page du chapitre *Contribuer* du syllabus. L'ensemble des
pages et chapitres du syllabus est regroupé dans le dossier ``pages/`` du syllabus. Voici la structure du dossier contenant
l'application web du syllabus, écrite en Python. Si vous désirez contribuer au contenu du syllabus, la partie qui vous
intéressera sera le dossier ``pages/``.

.. code-block::

    .
    ├── dependencies
    ├── README.md
    ├── static
    │   └── ...
    ├── syllabus
    │   ├── config.py
    │   ├── doc
    │   │   └── CREATE.md
    │   ├── inginious_syllabus.py
    │   ├── __init__.py
    │   ├── pages
    │   │   ├── toc.yaml
    │   │   ├── index.rst
    │   │   ├── chapitre_exemple
    │   │   │   └── ...
    │   │   └── contribuer
    │   │       └──contribuer.rst
    │   ├── static
    │   │   └── ...
    │   ├── templates
    │   │   └── ...
    │   └── utils
    │       └── ...
    └── syllabus-webapp.py

Dans le dossier ``pages/``, les chapitres sont les dossiers ``chapitre_exemple/`` et ``contribuer/``. Le fichier ``contribuer.rst``
est une page du chapitre ``contribuer/``

La table des matières du syllabus
=================================
La table des matières du syllabus, élément important de l'application, se trouve dans le fichier ``toc.yaml``. Elle contient
une description des chapitres et pages accessibles dans le syllabus. Si vous désirez créer un nouveau chapitre ou une nouvelle page,
vous devrez aussi les ajouter dans la table des matières.



Exemple: ajouter un nouveau chapitre et une nouvelle page dans ce chapitre
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Imaginons que le fichier ``toc.yaml`` contienne pour le moment ceci :

.. code-block:: yaml

    chapitre_exemple:       # pour représenter un chapitre, on met le nom du dossier de ce chapitre présent dans le dossier page
      title: "Chapitre d'exemple"       # Donner un nom human-readable au chapitre
      content:                          # Contient une liste des pages du chapitre
        theorie:            # pour représenter une page, on met le nom du fichier (sans le ".rst") contenant le texte de la page
          title: "Exemple de théorie"   # Donner un nom human-readable à la page
        qcm:                # une autre page pour le chapitre "chapitre_exemple"
          title: "Exemple de QCM"
      chapter_intro_file: "chapter_description.rst"     #   Fichier contenant un texte d'introduction qui sera affiché sur la page d'index du chapitre
    contribuer:             # un autre chapitre du syllabus
      title: Contribuer
      content:
        contribuer:         # la page que vous lisez actuellement
          title: Contribuer au contenu du syllabus

et que le contenu du dossier ``pages/`` du syllabus soit celui-ci:

.. code-block::

    pages
    ├── toc.yaml
    ├── chapter_index.rst
    ├── index.rst
    ├── chapitre_exemple
    │   ├── chapter_description.rst
    │   ├── qcm.rst
    │   └── theorie.rst
    └── contribuer
        └── contribuer.rst


Vous pouvez déjà constater que la syntaxe ``YAML`` est plutôt permissive (on peut omettre les guillemets par exemple). Imaginons
maintenant que l'on désire ajouter le chapitre ``chap1`` ainsi qu'une page pour ce chapitre, ``page1``.

Créer le dossier du chapitre et le fichier de la page
*****************************************************
La première chose à faire sera de créer le dossier ``chap1/`` représentant le chapitre dans le dossier ``pages/``,
ainsi qu'un fichier ``page1.rst`` à l'intérieur de ``chap1/`` qui contiendra le texte de la page
(le fichier peut être vide pour le moment). **N'oubliez pas l'extension** ``.rst`` **dans le nom de fichier**
``page1.rst`` **!**

Voici ce à quoi ressemblera le contenu du dossier ``pages/`` après l'ajout du dossier ``chap1/`` et du fichier ``page1.rst`` :


.. code-block::

    pages
    ├── toc.yaml
    ├── chapter_index.rst
    ├── index.rst
    ├── chapitre_exemple
    │   ├── chapter_description.rst
    │   ├── qcm.rst
    │   └── theorie.rst
    ├── contribuer
    │   └── contribuer.rst
    └── chap1               # dossier ajouté
        └── page1.rst       # fichier ajouté


Ajouter le chapitre et la page à la table des matières
******************************************************

Il ne reste maintenant plus qu'à ajouter le chapitre et la page à la table des matières pour qu'ils deviennent accessibles
sur le site. Il suffit de

- ajouter une entrée du nom du dossier du chapitre (``chap1``)
- donner au chapitre  un titre human-readable,
- ajouter la page en tant que contenu du chapitre (en la désignant par son nom de fichier, sans l'extension ``.rst``)
- donner un titre human-readable à la page

Concrètement, voici à quoi ressemblera ``toc.yaml`` après l'ajout du chapitre et de la page :



.. code-block:: yaml

    chapitre_exemple:
      title: "Chapitre d'exemple"
      content:
        theorie:
          title: "Exemple de théorie"
        qcm:
          title: "Exemple de QCM"
      chapter_intro_file: "chapter_description.rst"
    contribuer:
      title: Contribuer
      content:
        contribuer:
          title: Contribuer au contenu du syllabus
    chap1:  # chapitre ajouté (nom du dossier)
      title: Mon nouveau Chapitre   # titre du chapitre
      content:
        page1:                      # page ajoutée (nom du fichier sans le ".rst")
          title: Ma nouvelle Page   # titre de la page


**And that's it !** Votre nouvelle page dans votre nouveau chapitre est maintenant accessible depuis le site web.

Compris ?
*********

Et si l'on vous demandait maintenant d'ajouter un chapitre dans un dossier nommé ``boucles``, avec le titre ``"Les boucles"``,
contenant une unique page dans le fichier ``while.rst``, avec pour titre ``"La boucle while"``, a quoi ressemblerait le
fichier ``toc.yaml`` final ? Voici le fichier ``toc.yaml`` de base, rajoutez-y les infos concernant le chapitre et la page sus-mentionnés !

.. inginious:: test_tuto_syllabus text/x-yaml

    chapitre_exemple:
      title: "Chapitre d'exemple"
      content:
        theorie:
          title: "Exemple de théorie"
        qcm:
          title: "Exemple de QCM"
      chapter_intro_file: "chapter_description.rst"
    contribuer:
      title: Contribuer
      content:
        contribuer:
          title: Contribuer au contenu du syllabus
    # la suite ?

Dans les prochaines pages du tutoriel, vous apprendrez à ajouter une tâche INGInious à l'intérieur de vos pages.
