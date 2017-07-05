
$(function() {
    if (typeof $nmbr_prop == 'undefined') {
        $nmbr_prop = Infinity;
    }
    $('.comment-feedback').not('.preproc').hide();
    $('ul.positive').before('<ul class="proposals"></ul>');
    $('ul.positive').each(function(index) {
        $(this).shuffle().children('li').first()
            .prependTo($(this).parent().children('ul.proposals'))
            .attr('class', 'correct');
    });
    $('ul.negative').each(function(index) {
        $(this).shuffle();
        $(this).children('li').slice(0, $nmbr_prop-1).each(function(index) {
            $(this)
            .prependTo($(this).parent().parent().children('ul.proposals'))
            .attr('class', 'false');
        });
    });
    $('ul.positive-multiple').before('<ul class="proposals-multiple"></ul>');
    $('ul.positive-multiple').each(function(index) {
        //$(this).shuffle();
        $(this).children('li').each(function(index) {
            $(this)
            .prependTo($(this).parent().parent().children('ul.proposals-multiple'))
            .attr('class','correct');
        });
    });
    $('ul.negative-multiple').each(function(index) {
        //$(this).shuffle();
        $(this).children('li').each(function(index) {
            $(this)
            .prependTo($(this).parent().parent().children('ul.proposals-multiple'))
            .attr('class','false');
        });
    });
    $('ul.proposals').each(function(index) {
        $(this).shuffle();
        $('<input type="radio" name="' + $(this).parent().attr('id') + '">').prependTo($(this).children('li'));
    });
    $('ul.proposals-multiple').each(function(index) {
        $('<input type="checkbox" name="' + $(this).parent().attr('id') + '">').prependTo($(this).children('li'));
    });
    $('ul.positive').hide();
    $('ul.negative').hide();
    $('ul.positive-multiple').hide();
    $('ul.negative-multiple').hide();
    $('#questionnaire-rst').append('<div id="checker" class="checker"><h1>Vérifiez vos réponses</h1><input type="submit" value="Vérifier" id="verifier"></div>');
    $('#verifier').click(function () {
        var nb_prop = $('ul.proposals').length + $('ul.proposals-multiple').length;
        var res = $('li.correct input:checked').length - $('li.false input:checked').length;
        if(res <0) {
            res = 0;
        }
        $('.comment-feedback').not('prepoc').show();
        $('.checkmark').remove();
        $('.result').remove();
        $('li.false input:checked').parent().prepend('<img class="checkmark" src="/static/images/false.png" style="display: none;"></img>');
        $('li.correct input:checked').parent().prepend('<img class="checkmark" src="/static/images/correct.png" style="display: none;"></img>');
        $('.checkmark').show();
        $('input:checked').parent().children('.comment').show('slow');
        $('#checker').append('<div class="result">Votre score est de ' +
                            res + '/' +
                            nb_prop + '</div>');
    });
    $('pre.literal-block').addClass('prettyprint');
});

