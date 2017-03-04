function submitCode(url, taskID, questionID, code, feedbackContainer, toDisable){
    var td = $(toDisable);
    td.attr("disabled", true);
    $.post(url, {'taskid': taskID, 'input': JSON.stringify({[questionID]: code})}, function(data) {
        parseRST(data.result[1], data.result[0], feedbackContainer, td);
    });
}

function parseRST(rst, status, feedbackContainer, toEnable){
    $.post("/parserst", {rst: rst}, function(data){
        var container = $(feedbackContainer);
        var result = data["result"];
        if(status == "failed"){
            container.removeClass("alert-success");
            container.addClass("alert-danger");
        }
        else if(status == "success"){
            container.removeClass("alert-danger");
            container.addClass("alert-success");
        }
        toEnable.attr("disabled", false);
        container.html(data);
        container.show();
    })
}