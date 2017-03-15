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

Regardons de plus près le code de ce programme. Nous allons le détailler dans les unités suivantes.


Exercice:

.. inginious::
