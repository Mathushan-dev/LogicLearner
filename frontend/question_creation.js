class Question {
    constructor(id, source, prompt, input_method, correct_grammar, correct_formula, prohibited_formula) {
        this.id = id;
        this.source = source;
        this.prompt = prompt;
        this.input_method = input_method;
        this.correct_grammar = correct_grammar;
        this.correct_formula = correct_formula;
        this.prohibited_formula = prohibited_formula;
    }

    to_json() {
        return {
            "id": this.id,
            "source": this.source,
            "prompt": this.prompt,
            "input_method": this.input_method,
            "correct_grammar": this.correct_grammar,
            "correct_formula": this.correct_formula,
            "prohibited_formula": this.prohibited_formula
        };
    }

    to_json_string() {
        return JSON.stringify(this.to_json())
    }
}

class QuestionSet {
    constructor(id, name, questions = []) {
        this.id = id;
        this.name = name;
        this.questions = questions;
    }

    to_json() {
        return {
            "id": this.id,
            "name": this.name,
            "questions": this.questions,
        };
    }

    to_json_string() {
        return JSON.stringify(this.to_json())
    }

    add_question(question) {
        this.questions.push(question);
    }
}

function sendQuestionSet(question_set) {
    return $.ajax({
        url: "http://127.0.0.1:8888/post_json",
        type: "POST",
        data: question_set.to_json_string(),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        async: false,
        success: function (response) {
            console.log("JSON sent");
            console.log("Question Set ID: " + response);
        },
        error: function () {
            console.log("JSON not sent");
        }
    }).responseText;
}

var question_array = [];

function submit_qs(name) {
    var questionSet = new QuestionSet("temp", name);
    for (let i = 0; i < question_array.length; ++i) {
        questionSet.add_question(new Question("temp", "custom question", question_array[i].prompt, question_array[i].input, question_array[i].grammar, question_array[i].formula, question_array[i].pformula))
    }
    
    id = sendQuestionSet(questionSet);
    var score = {
        "name": questionSet.name,
        "code": id,
        "score": "[created]",
    };
    localStorage.setItem(new Date().getTime(), JSON.stringify(score));

    alert("Question Set ID: " + id);
    window.location.href = "landing.html";
}

function add_q() {
    var question = {
        title: document.getElementById("title").value,
        prompt: document.getElementById("prompt").value,
        grammar: document.getElementById("grammar").value,
        formula: document.getElementById("formula").value,
        pformula: document.getElementById("p_formula").value,
        input: document.getElementById("input_method").value
    };
    question_array.push(question);

    document.getElementById("titles").style.columnWidth = "auto";
    document.getElementById("grammars").style.columnWidth = "auto";
    document.getElementById("inputs").style.columnWidth = "auto";
    document.getElementById("deletions").style.columnWidth = "auto";

    var table = document.getElementById("questions");
    var new_row = table.insertRow(question_array.length);
    new_row.onclick = function () {
        console.log("hello");
    };
    var title = new_row.insertCell();
    var grammar = new_row.insertCell();

    var input = new_row.insertCell();
    var delete_question = new_row.insertCell();
    title.innerHTML = question.prompt;
    grammar.innerHTML = question.grammar;

    input.innerHTML = question.input;
    //new_row.addEventListener();
    var btn = document.createElement('input');
    btn.type = "button";
    btn.className = "btn btn-danger btn-sm";
    btn.value = "X";
    btn.onclick = function () {

        var td = event.target.parentNode;
        var tr = td.parentNode; // the row to be removed
        tr.parentNode.removeChild(tr);

        question_array = question_array.filter(function (value, index, arr) {
            return value != question;
        })

    };
    delete_question.appendChild(btn);

   document.getElementById("prompt").value = "";
   document.getElementById("formula").value = "";
   document.getElementById("p_formula").value = "";
}

function add_cookie(question_number, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = question_number + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(question_number) {
    var name = question_number + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}