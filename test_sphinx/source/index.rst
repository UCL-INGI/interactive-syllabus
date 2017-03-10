.. test documentation master file, created by
   sphinx-quickstart on Wed Mar  8 23:16:01 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Test intégration tâche INGInious
================================

.. raw:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
        <script src="/static/js/jquery-3.1.1.min.js"></script>
        <link href="/static/css/bootstrap.min.css" rel="stylesheet">
        <script src="/static/js/bootstrap.min.js"></script>
        <link rel="stylesheet" href="/static/css/codemirror.css">

        <script src="/static/js/codemirror.js"></script>
        <script src="/static/js/codemirror-clike-style.js"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
    <div class="container">
        <span id="maincontent"></span>
        <h2>Parler java : syntaxe de base</h2>
        <h3>Syntaxe - commentaires</h3>
        <div class="box contents" id="yui_3_17_2_1_1488494895295_113">
            <div class="no-overflow" id="yui_3_17_2_1_1488494895295_112"><p>Java est un <strong>langage de
                programmation</strong>. Au travers d'une grammaire bien précise, il permet d'écrire dans un fichier texte
                une suite d'instructions. Ce texte, appelé <strong>code source</strong>, est la base d'un
                <strong>programme</strong> informatique capable d'accomplir vos rêves les plus fous.&nbsp;</p>
                <p>Le fichier dans lequel le code source se trouve a une
                    extension&nbsp;<code>.java </code>(<strong></strong>pour notre exemple, ce serait&nbsp;
                    <code>Hello.java</code>). Il sera compilé par un programme (<code>javac</code>) qui, entre autres,
                    vérifiera que le texte qu'il contient respecte bien la <strong>syntaxe</strong> prévue. Sans quoi,
                    <code>javac</code> ne sera pas à même de comprendre le code source. Un peu comme si il manquait un verbe
                    dans une phrase.</p>
                <p>Cette syntaxe, cette grammaire, cette façon d'écrire en java a toute son importance et vous l'apprendrez
                    en détails dans les différentes unités de ce cours.</p>
                <p>Mais puisqu'il faut bien commencer quelque part et parce que c'est la coutume, nous allons détailler
                    ensemble un premier programme complet :</p>
                <pre id="yui_3_17_2_1_1488494895295_117"><code id="yui_3_17_2_1_1488494895295_116">/*<br>&nbsp;* Un programme qui affiche Hello, world!<br>&nbsp;*/ <br>public class Hello {<br>&nbsp;&nbsp; public static void main (String[] args) {<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; // affiche à l’écran<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; System.out.println("Hello, world !");<br>&nbsp;&nbsp; } // fin de main<br>} // fin de la classe Hello</code></pre>
                <p>Ce programme va afficher <code>Hello, world !</code>.</p>
                <p>Pour les non novices, si vous êtes déjà capable de comprendre entièrement cet exemple, il est conseillé
                    de passer directement à la section suivante.</p>
                <p>Regardons de plus près le code de ce programme. Nous allons le détailler dans les unités suivantes.</p>
            </div>
        </div>
        <div class="box branchbuttoncontainer horizontal">
            <div class="singlebutton">
                <form method="post" action="https://moodleucl.uclouvain.be/mod/lesson/continue.php">
                    <div><input type="submit" value="page suivante"><input type="hidden" name="id" value="601400"><input
                            type="hidden" name="pageid" value="256890"><input type="hidden" name="sesskey"
                                                                              value="tNe5eewCUl"><input type="hidden"
                                                                                                        name="jumpto"
                                                                                                        value="-1"></div>
                </form>
            </div>
        </div>
        <h2>Exercise time !</h2>
        Mettez maintenant en pratique ce que vous venez de voir !
        Pour vous entraîner à l'utilisation de boucles for, écrivez une boucle for qui permettra de calculer la somme des n premiers entier PAIRS supérieurs à zéro, en fonction de la variable n, déjà définie à une valeur supérieure ou égale à zéro. Le résultat final doit être stocké dans la variable sum à la fin de la boucle, elle aussi déjà définie. Lorsque n est négatif, le résultat doit valoir zéro.
        <pre>
        int n = /* n peut prendre n'importe quelle valeur */
        int sum = 0;</pre>
        Écrivez ici le bout de programme permettant de calculer la somme des n premiers entiers pairs :
        <div id="feedback-container" class="alert alert-success" hidden>
            <strong>Success!</strong> Indicates a successful or positive action.
        </div>
        <form method="post" id="form1" action="http://localhost:8080/tutorial">
            <textarea style="width:100%; height:150px;" id="code" name="code"></textarea><br/>
            <input type="text" name="taskid" id="taskid" value="syllabus-test" hidden/>
            <input type="text" name="input" id="to-submit" hidden/>
        </form>
        <button class="btn btn-primary" id="b1" value="Submit">Submit</button>
    </div>
    </body>
    <script src="/static/js/submitter.js"></script>
    <script>
        var editor = CodeMirror.fromTextArea(document.getElementById('code'), {
            lineNumbers: true,
            matchBrackets: true,
            mode: "text/x-java"
        });
        $('#b1').click(function(e){
            var toSubmit = editor.getValue();
            var taskID = $('#taskid').val();
            $('#to-submit').val(JSON.stringify({q1: toSubmit}));
            submitCode("{{ inginious_url }}/tutorial", taskID, "q1", toSubmit, $('#feedback-container'), $('#code'));
        });
    </script>
    </html>
