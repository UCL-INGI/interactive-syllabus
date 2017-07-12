.. Cette page est publiée sous la license Creative Commons BY-SA (https://creativecommons.org/licenses/by-sa/3.0/fr/)

.. author::

    Alexandre Dubray

=========================
Créer une tâche INGInious
=========================

Les pages du syllabus sont constituées d'une partie de **théorie** et d'une partie d'**exercice**. L'ajout d'un exercice
se fait en deux étapes.

Étape 1. Créer l'exercice INGInious
===================================

La première étape consiste à créer l'exercice INGInious. Un exercice INGInious est un dossier dont la structure minimale est la suivante:

.. code-block::

    .
    ├── task.yaml # Fichier contenant la configuration de la tâches.
    ├── run # Script de lancement des tests et d'envoie du résultat
    └── student # Dossier dans lequel sera exécuté la soumission de l'étudiant.
        └── ...

**Attention** les tâches que vous créez doivent se trouver dans le dossiers ``[inginious_path]/tutorial``, où ``[inginious_path]``
est le chemin jusqu'à l'endroit dans lequel vous stockez vos cours (voir installation d'INGInious).

Vous pouvez créer les tâches facilement via l'interface graphique d'INGInious.

Dans le dossier ``student/`` se trouveront les tests unitaires de la tâche ainsi qu'un fichier qui servira de
réceptacle pour le code de l'étudiant. De plus, il est important de noter que lors de l'exécution des tests, le programme n'aura accès
qu'à ce qui se trouve dans ``student/``.

Étape 2. Insérer la tâche dans le fichier .rst
==============================================

Une fois que vôtre tâche est créée, vous devez l'insérer dans votre page écrite en rST. Pour cela, il suffit simplement d'utiliser la directive
rST **inginious**. Supposons que nous avons une tâche nommée ``test``. Nous pouvons alors l'inclure dans la page de théorie via le bout de code suivant:

.. code-block:: rst

    .. inginious:: test


Si en plus, vous désirez pré-remplir un bout de code dans l'encadré de la tâche, vous pouvez rajouter bout de code de la manière suivante:

.. code-block:: rst

    .. inginious:: test
        // exemple de bout de code
        public static void main(String [] args) {
            int i = 1;
            /* à compléter par l'étudiant */
        }
