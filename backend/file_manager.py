import json
import typing
import random
import os
import re

import backend.logic_engine


class Question:
    def __init__(self, identifier: str, source: str, prompt: str, input_method: str, correct_grammar: str,
                 correct_formula: str, prohibited_formula: str) -> typing.NoReturn:
        # User created/generated etc.
        self.__id = identifier
        self.__source: str = source
        self.__prompt: str = prompt
        self.__input_method: str = input_method
        # Identifies type of formula (prop logic, boolean etc.)
        self.__correct_grammar: str = correct_grammar
        # The answer
        self.__correct_formula: str = correct_formula
        self.__prohibited_formula: str = prohibited_formula

    @property
    def to_dict(self) -> dict:
        dictionary: typing.Dict[str, str] = {'id': self.__id,
                                             'source': self.source,
                                             'prompt': self.prompt,
                                             'input_method': self.input_method,
                                             'correct_grammar': self.correct_grammar,
                                             'correct_formula': self.correct_formula,
                                             'prohibited_formula': self.prohibited_formula}
        return dictionary

    @property
    def to_json_string(self) -> str:
        return json.dumps(self.to_dict)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def source(self) -> str:
        return self.__source

    @property
    def prompt(self) -> str:
        return self.__prompt

    @property
    def input_method(self) -> str:
        return self.__input_method

    @property
    def correct_grammar(self) -> str:
        return self.__correct_grammar

    @property
    def correct_formula(self) -> str:
        return self.__correct_formula

    @property
    def prohibited_formula(self) -> str:
        return self.__prohibited_formula


class QuestionSet:
    def __init__(self, identifier: str, name: str, questions: typing.List[Question] = None) -> typing.NoReturn:
        if questions is None:
            questions = []
        self.__id: str = identifier
        self.__name: str = name
        self.__questions: typing.List[Question] = []
        for question in questions:
            self.add_question(question)

    def add_question(self, question: Question) -> typing.NoReturn:
        if not self.__check_question_id_unique(question.id):
            raise NonUniqueQuestionIdError
        self.__questions.append(question)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def questions(self) -> typing.List[Question]:
        return self.__questions

    @property
    def to_dict(self) -> dict:
        dictionary: typing.Dict[str, str] = {'id': self.id,
                                             'name': self.name,
                                             'questions': [question.to_dict for question in self.questions]}
        return dictionary

    @property
    def to_json_string(self) -> str:
        return json.dumps(self.to_dict)

    def set_id(self, identifier: str) -> typing.NoReturn:
        self.__id = identifier

    def __check_question_id_unique(self, identifier: str) -> bool:
        for question in self.questions:
            if question.id == identifier:
                return False
        return True

    def get_question_by_id(self, identifier: str) -> typing.Optional[Question]:
        for question in self.questions:
            if question.id == identifier:
                return question
        return None


class NonUniqueQuestionIdError(Exception):
    pass


class FileManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def retrieve_from_file(self, identifier: str, hide_answer: bool) -> QuestionSet:
        with open(f'{self.data_dir}/{identifier}.json', 'r') as file:
            question_contents: dict = json.load(file)
        question: dict
        if hide_answer:
            for question in question_contents['questions']:
                if question['input_method'] == 'Text':
                    question['correct_formula'] = ""
                elif question['input_method'] == 'Blocks':
                    question['correct_formula'] = self.__shuffle_answer(question['correct_formula'])
        return dict_to_question_set(question_contents)

    # Returns id of generated question
    def write_to_file(self, question_set: QuestionSet) -> str:
        identifier: str = self.__generate_unique_set_id()
        question_set.set_id(identifier)
        file: typing.TextIO
        with open(f'{self.data_dir}/{identifier}.json', 'w') as file:
            json.dump(question_set.to_dict, file, indent=1)
        return identifier

    def __generate_unique_set_id(self) -> str:
        while True:
            code: str = ""
            for _ in range(6):
                code += random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
            if not os.path.isfile(f'{self.data_dir}/{code}.json'):
                return code

    @staticmethod
    def __shuffle_answer(answer: str):
        answer = re.sub('<->', '↔', answer)
        answer = re.sub('->', '→', answer)
        answer = re.sub('<-', '←', answer)
        answer = re.sub(' ', '', answer)
        answer_as_list: list = list(answer)
        random.shuffle(answer_as_list)
        answer = ''.join(answer_as_list).replace("", " ")[1:-1]
        answer = re.sub('↔', '<->', answer)
        answer = re.sub('→', '->', answer)
        answer = re.sub('←', '<-', answer)
        return answer


class InvalidJsonFormatError(Exception):
    pass


def json_to_question_set(json_string: str) -> QuestionSet:
    question_contents: dict = json.loads(json_string)
    for i in range(len(question_contents['questions'])):
        question_contents['questions'][i]['id'] = str(i)
    return dict_to_question_set(question_contents)


def dict_to_question_set(question_set: dict) -> QuestionSet:
    try:
        return QuestionSet(question_set['id'],
                           question_set['name'],
                           [Question(question['id'],
                                     question['source'],
                                     question['prompt'],
                                     question['input_method'],
                                     question['correct_grammar'],
                                     question['correct_formula'],
                                     question['prohibited_formula'])
                            for question in question_set['questions']])
    except KeyError:
        raise InvalidJsonFormatError("JSON formatting incorrect")


def generate_random_questions(count: int) -> QuestionSet:
    questions: QuestionSet = QuestionSet("temp", "Random Question Set")
    i: int
    for i in range(count):
        questions_tuple: typing.Tuple[str, str, str, str, str] = backend.logic_engine.generate_question()
        questions.add_question(
            Question(str(i), "randomly generated", questions_tuple[3], questions_tuple[4], questions_tuple[0],
                     questions_tuple[1], questions_tuple[2]))
    return questions


def test() -> typing.NoReturn:
    file_manager: FileManager = FileManager('../data')
    question: Question = Question('1', 'b', 'c', 'd', 'e', 'f', 'g')
    question2: Question = Question('2', 'b', 'c', 'd', 'e', 'f', 'g')
    questionset: QuestionSet = QuestionSet('a', 'b', [question, question2])
    print(questionset.id, questionset.name)
    for q in questionset.questions:
        print(q.prompt)
    print(questionset.to_dict)
    print(questionset.to_json_string)
    file_manager.write_to_file(questionset)
    print(file_manager.retrieve_from_file('362684').questions.pop().to_dict)
    print(generate_random_questions(10).to_dict)


if __name__ == '__main__':
    test()
