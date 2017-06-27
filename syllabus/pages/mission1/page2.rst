.. name: Viens faire un qcm!

.. This file is an example of MCQ.

.. These scripts are needed for executing the mcq

.. raw:: html

  <script type="text/javascript" src="static/js/jquery-3.1.1.min.js"></script>
  <script type="text/javascript" src="static/js/jquery-shuffle.js"></script>
  <script type="text/javascript" src="static/js/rst-form.js"></script>
  <script type="text/javascript" src="static/js/prettify.js"></script>
.. This variable hold the number of proposition shown to the student

  <script type="text/javascript">$nmbr_prop = 3</script>

Question 1. Analyse de code
---------------------------

Quelle est la valeur dans la variable ``x`` après l'exécution de ce code ?

.. code-block:: java

    public static void compute() {
        int x;
        int y = 10;
        int z = 20;
        if (z % y == 0) {
            x = 2;
        } else {
            x = 3;
        }
    }

.. The positive class group all the correct value to the question while the negative hold all the incorrect answer

.. class:: positive

    - 2

.. class:: negative

    - 3

Question 2. Signature de fonction
---------------------------------

Parmis les propositions, quelle est la signature compatible avec le corps de la fonction suivante

.. code-block:: java

    <signature> {
        int x = 2;
        return x+y;
    }

.. class:: positive

    - public static int Compute(int y)

.. class:: negative

    - public static int Compute(boolean y)
    - public static String Compute(int y)
    - public static int Compute(int z)

Question 3. Portée des variables
--------------------------------

Lorsque l'on écrit un programme, il est préférable de ne pas avoir plusieurs variables portant le même nom dans des portée lexicale différentes. Que va afficher
le programme ci-dessous? La méthode ``Show`` est appelée avec ``42`` comme argument

.. code-block:: java

    /* Variables globales */
    int i = 12;
    int j = 24;

    public static void Show(int j){
        System.out.println("I:"+i);
        System.out.println("J:"+j);
        int i;
        for(i= 0;i < 10;i++){
            /* Do something */
        }
        System.out.println("I:"+i);
    }

.. class:: positive

    -
        .. code-block:: console

            I:12
            J:42
            I:10

.. class:: negative

    -
        .. code-block:: console

            I:12
            J:24
            I:10
    -
        .. code-block:: console

            I:12
            J:42
            I:12

.. This line include the "check your answer" button that gives a note to the student and mark questions with the
    correct marker if the answer is to good one, or the incorrect marker if not.

.. raw:: html

    <div id="checker" class="checker"><h1>Vérifiez vos réponses</h1><input type="submit" value="Vérifier" id="verifier"></div>

