function submitCode(url, taskID, questionID, code, feedbackContainer, task,editor){

    $(task).not('.loadingdiv').css("opacity",0.5);
    editor.setOption("readOnly",true);

    $(task).find('.loadingdiv').show();

    $.post(url, {'taskid': taskID, 'input': JSON.stringify({[questionID]: code})}, function(data) {
        let toParse = data.result[1];
        for(let property in data.problems){
            toParse += "\n\n" + data.problems[property];
        }
        console.log(toParse);
        parseRST(toParse, data.result[0], feedbackContainer, task, editor);
    });
}

function parseRST(rst, status, feedbackContainer, task, editor){
    $.post("/parserst", {rst: rst}, function(data){
        let container = $(feedbackContainer);
        let result = data["result"];
        console.log("data:");
        console.log(data);
        if(status == "failed"){
            container.removeClass("alert-success");
            container.addClass("alert-danger");
        }
        else if(status == "success"){
            container.removeClass("alert-danger");
            container.addClass("alert-success");
        }
        $(task).css("opacity",1);
        editor.setOption("readOnly",false);
        $(task).find('.loadingdiv').hide();
        container.html(data);
        container.show();
    })
}