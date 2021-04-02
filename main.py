import flask
import flask_cors
import backend.file_manager
import backend.logic_engine

app: flask.Flask = flask.Flask(__name__)
flask_cors.CORS(app)
file_manager: backend.file_manager.FileManager = backend.file_manager.FileManager('data')


@app.route('/post_json', methods=['POST'])
def post_json():
    if flask.request.method == 'POST':
        return file_manager.write_to_file(backend.file_manager.json_to_question_set(flask.request.get_data().decode()))


@app.route('/get_json', methods=['GET'])
def get_json():
    if flask.request.method == 'GET':
        return file_manager.retrieve_from_file(flask.request.headers.get('identifier'), hide_answer=True).to_json_string


@app.route('/random', methods=['GET'])
def get_random_question_set():
    if flask.request.method == 'GET':
        set_id: str = file_manager.write_to_file(
            backend.file_manager.generate_random_questions(int(flask.request.headers.get('question_count'))))
        return file_manager.retrieve_from_file(set_id, hide_answer=True).to_json_string


@app.route('/mark_answer', methods=['GET'])
def mark_answer():
    if flask.request.method == 'GET':
        question_set = file_manager.retrieve_from_file(flask.request.headers.get('set_id'), hide_answer=False).get_question_by_id(
            flask.request.headers.get('question_id'))
        return backend.logic_engine.validate_answer(flask.request.headers.get('user_answer'),
                                                    question_set.correct_formula, question_set.prohibited_formula,
                                                    question_set.correct_grammar)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8888, debug=True)
