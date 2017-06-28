.. author::

    John Doe

=============================
Parler java : syntaxe de base
=============================
----------------------
Syntaxe - commentaires
----------------------
Java est un **langage de programmation**. Au travers d'une grammaire bien précise, il permet d'écrire dans un fichier texte
une suite d'instructions. Ce texte, appelé **code source**, est la base d'un **programme** informatique capable d'accomplir vos rêves les plus fous.


Le fichier dans lequel le code source se trouve a une extension ``.java`` (pour notre exemple, ce serait ``Hello.java``). Il sera compilé par un programme (``javac``) qui, entre autres,
vérifiera que le texte qu'il contient respecte bien la **syntaxe** prévue. Sans quoi, ``javac`` ne sera pas à même de comprendre le code source. Un peu comme s'il manquait un verbe
dans une phrase.

Cette syntaxe, cette grammaire, cette façon d'écrire en java a toute son importance et vous l'apprendrez en détails dans les différentes unités de ce cours.


Mais puisqu'il faut bien commencer quelque part et parce que c'est la coutume, nous allons détailler
ensemble un premier programme complet :

.. code-block:: java

        /*
         * Un programme qui affiche Hello, world!
         */
         public class Hello {
             public static void main (String[] args) {
                 // affiche à l’écran
                 System.out.println("Hello, world !");
             } // fin de main
         } // fin de la classe Hello

Ce programme va afficher ``Hello, world !``.

Pour les non novices, si vous êtes déjà capable de comprendre entièrement cet exemple, il est conseillé
    de passer directement à la section suivante.

Pour les autres, êtes-vous capables de modifier ce petit programme pour afficher ``"Bonjour !"`` au lieu de ``"Hello, world !"`` ?

Essayez donc :

.. inginious:: syllabus-bonjour

        /*
         * Un programme qui affiche Hello, world!
         */
         public class Hello {
             public static void main (String[] args) {
                 // affiche à l’écran
                 System.out.println("Hello, world !");
             } // fin de main
         } // fin de la classe Hello



Nous allons détailler ce programme dans les unités suivantes.

Exercise
********
Mettez maintenant en pratique ce que vous venez de voir !
Pour vous entraîner à l'utilisation de boucles for, écrivez une boucle for qui permettra de calculer la somme des n premiers entier PAIRS supérieurs à zéro, en fonction de la variable n, déjà définie à une valeur supérieure ou égale à zéro. Le résultat final doit être stocké dans la variable sum à la fin de la boucle, elle aussi déjà définie. Lorsque n est négatif, le résultat doit valoir zéro.

.. code-block:: java

    int n = /* n peut prendre n'importe quelle valeur */
    int sum = 0;

Remplissez les trous du bout de programme permettant de calculer la somme des n premiers entiers pairs :

.. inginious:: syllabus-integer-sum

    for(int i = /*1*/ ; i <= n ; /*2*/){
        sum += /*3*/;
    }

.. author::

    Michel François
