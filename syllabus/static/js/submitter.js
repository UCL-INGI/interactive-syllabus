function submitCode(url, taskID, questionID, code, feedbackContainer, task,editor){
    $(task).not('.loadingdiv').css("opacity",0.5);
    editor.setOption("readOnly",true);

    var container = $(feedbackContainer);
    container.removeClass("alert-success");
    container.removeClass("alert-danger");
    container.addClass("alert-info");
    container.html("<i id='loading-spinner' class=\"glyphicon glyphicon-refresh glyphicon-spin\"></i> Envoi de votre code...");
    container.show();

    $.post(url, {'taskid': taskID, 'input': JSON.stringify({[questionID]: code})}, function(data) {
        let toParse = data.result[1];
        for(let property in data.problems){
            toParse += "\n\n" + data.problems[property];
        }
        parseRST(toParse, data.result[0], feedbackContainer, task, editor);
    });

}

function parseRST(rst, status, feedbackContainer, task, editor){
    $.post("/parserst", {rst: rst}, function(data){
        var container = $(feedbackContainer);
        container.html('');
        if(status == "failed"){
            container.removeClass("alert-success");
            container.removeClass("alert-info");
            container.addClass("alert-danger");
        }
        else if(status == "success"){
            container.removeClass("alert-danger");
            container.removeClass("alert-info");
            container.addClass("alert-success");
        }
        $(task).css("opacity",1);
        editor.setOption("readOnly",false);
        container.html(data);
        container.show();
    })
}