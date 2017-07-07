
function parse_question(pattern, object, bool) {

	$(this).shuffle();
	$(object).children('li').each(function(index) {
		$(this)
		.prependTo($(this).parent().parent().children(pattern))
		.attr('class',bool);
	});
}

$(function () {

	$('.comment-feedback').hide();
	/* Classical treatment */
	$('ul.positive').before('<ul class="proposals"></ul>');
	$('ul.positive').each(function(index) {
		parse_question('ul.proposals',$(this), 'correct');
	});
	$('ul.negative').each(function(index) {
		parse_question('ul.proposals',$(this), 'false');
	});

	/* Multiple selection treatment */
	$('ul.positive-multiple').before('<ul class="proposals-multiple"></ul>');
	$('ul.positive-multiple').each(function(index) {
		parse_question('ul.proposals-multiple',$(this),'correct');
	});
	$('ul.negative-multiple').each(function(index) {
		parse_question('ul.proposals-multiple',$(this),'false');
	});

	/* Treatment of proposals */

    $('ul.proposals').each(function(index) {
        $('<input type="radio" name="' + $(this).parent().attr('id') + '">').prependTo($(this).children('li'));
    });
    $('ul.proposals-multiple').each(function(index) {
        $('<input type="checkbox" name="' + $(this).parent().attr('id') + '">').prependTo($(this).children('li'));
    });

	$('#questionnaire-rst').append('<div id="checker" class="checker"><h1>Vérifier vos réponses</h1><input type="submit" value="Vérifier" id="verifier"></div>');
	$('#verifier').click(function() {
	    $('.comment-feedback').hide();
		var nb_prop = $('ul.proposals').length + $('ul.proposals-multiple').length;
		var res = $('li.correct input:checked').length - $('li.false input:checked').length;
		if(res < 0) {
			res = 0;
		}
		$('.checkmark').remove();
		$('.result').remove();
		$('li.false input:checked').parent().prepend('<img class="checkmark" src="/static/images/false.png" style="display: none;"></img>');
		$('li.correct input:checked').parent().prepend('<img class="checkmark" src="/static/images/correct.png" style="display: none;"></img>');
		$('.checkmark').show();
		$('input:checked').parent().children('.comment-feedback').show('slow');
		$('#checker').append('<div class="result">Votre score est de ' + res + '/' + nb_prop + '</div>');
	});
	$('pre.literal-block').addClass('prettyprint');
});
