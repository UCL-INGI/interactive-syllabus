function submitCode(url, taskID, questionID, code, feedbackContainer, toDisable){
    let td = $(toDisable);
    td.attr("disabled", true);
    $.post(url, {'taskid': taskID, 'input': JSON.stringify({[questionID]: code})}, function(data) {
        let toParse = data.result[1];
        for(let property in data.problems){
            toParse += "\n\n" + data.problems[property];
        }
        console.log(toParse);
        parseRST(toParse, data.result[0], feedbackContainer, td);
    });
}

function parseRST(rst, status, feedbackContainer, toEnable){
    $.post("/parserst", {rst: rst}, function(data){
        let container = $(feedbackContainer);
        let result = data["result"];
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