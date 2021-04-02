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

class AttemptingQuestionSet {
    constructor(id, name, questions = [], currentIndex, currentScore) {
        this.id = id;
        this.name = name;
        this.questions = questions;
        this.currentQuestionIndex = currentIndex;
        this.score = currentScore;
        console.log(this.to_json());
    }

    to_json() {
        return {
            "id": this.id,
            "name": this.name,
            "questions": this.questions,
            "currentQuestionIndex": this.currentQuestionIndex,
            "score": this.score
        };
    }

    increase_score() {
        this.score = this.score + 1;
    }

    to_json_string() {
        return JSON.stringify(this.to_json());
    }

    hasNextQuestion() {
        return this.currentQuestionIndex < this.questions.length;
    }

    viewNextQuestion() {
        return this.questions[this.currentQuestionIndex];
    }

    add_question(question) {
        this.questions.push(question);
    }

    get_next_question() {
        if (this.currentQuestionIndex >= this.questions.length) {
            return null;
        }
        const question = this.questions[this.currentQuestionIndex];
        this.currentQuestionIndex = this.currentQuestionIndex + 1;
        return question;
    }
}

class QuestionSet {
    constructor(id, name, questions = []) {
        this.id = id;
        this.name = name;
        this.questions = questions;
        this.currentQuestionIndex = 0;
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

    get_next_question() {
        console.log("hello?");
        if (this.currentQuestionIndex >= this.questions.length) {
            return null;
        }
        const question = this.questions[this.currentQuestionIndex];
        this.currentQuestionIndex++;
        return question;
    }
}

function getQuestionSet(identifier) {
    return JSON.parse($.ajax({
        url: "http://127.0.0.1:8888/get_json",
        type: "GET",
        headers: {'identifier': identifier},
        async: false,
        success: function (response) {
            console.log("JSON received");
            let question_json = JSON.parse(response);
            let question_set = new QuestionSet(question_json.id, question_json.name, question_json.questions.map(i => new Question(i.id, i.source, i.prompt, i.input_method, i.correct_grammar, i.correct_formula, i.prohibited_formula)));
            console.log(question_set);
            return question_set;
        },
        error: function () {
            console.log("JSON not received");
        }
    }).responseText);
}

function getRandomQuestionSet(question_count) {
    return JSON.parse($.ajax({
        url: "http://127.0.0.1:8888/random",
        type: "GET",
        headers: {'question_count': question_count},
        async: false,
        success: function (response) {
            console.log("JSON received");
            let question_json = JSON.parse(response);
            let question_set = new QuestionSet(question_json.id, question_json.name, question_json.questions.map(i => new Question(i.id, i.source, i.prompt, i.input_method, i.correct_grammar, i.correct_formula, i.prohibited_formula)));
            console.log(question_set);
            return question_set;
        },
        error: function () {
            console.log("JSON not received");
        }
    }).responseText);
}

function getQuestionAnswer(setId, questionId, userAnswer) {
    return $.ajax({
        url: "http://127.0.0.1:8888/mark_answer",
        type: "GET",
        headers: {'set_id': setId, 'question_id': questionId, 'user_answer': userAnswer},
        async: false,
        success: function (response) {
            console.log("Answer received: ", response);
        },
        error: function () {
            console.log("Answer not received");
        }
    }).responseText;
}