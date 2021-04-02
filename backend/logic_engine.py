from lark import Lark, Tree, Token, Transformer, Visitor, LarkError
from typing import Dict, Callable, List, Tuple
import random

prop_parser = Lark(r"""
    formula : formula"<->"formula -> equivalent
            | formula"->"formula -> implies
            | formula"<"formula -> _or
            | formula"^"formula -> _and
            | "-("formula")" -> not_formula
            | "("formula")" -> brackets
            | LETTER -> letter
            | "-"LETTER -> not_letter
    
    LETTER : /[a-zA-Z]/

    %import common.WS
    %ignore WS
""", start='formula')

bool_parser = Lark(r"""
    formula : formula"+"formula -> _or
            | formula"."formula -> _and
            | "-("formula")" -> not_formula
            | "("formula")" -> brackets
            | LETTER -> letter
            | "-"LETTER -> not_letter

    LETTER : /[a-zA-Z]/

    %import common.WS
    %ignore WS
""", start='formula')

dnf_parser = Lark(r"""
    disjunction : conjunction"<"disjunction -> _or
                | conjunction -> brackets

    conjunction : "("literal"^"conjunction")" -> _and
                | literal -> brackets

    literal : LETTER -> letter
            | "-"LETTER -> not_letter

    LETTER : /[a-zA-Z]/

    %import common.WS
    %ignore WS
""", start='disjunction')

# evaluate tree bottom-up with logical operators based on valuation
def evaluate_tree(tree: Tree, valuation: Dict[str, bool]) -> bool:
    class Evaluator(Transformer):
        def letter(self, tok: Token) -> bool:
            return valuation[tok[0].value]
        def brackets(self, tree: Tree) -> bool:
            return tree[0]
        def not_letter(self, tok: Token) -> bool:
            return not valuation[tok[0].value]
        def not_formula(self, tree: Tree) -> bool:
            return not tree[0]
        def _and(self, tree: Tree) -> bool:
            return tree[0] and tree[1]
        def _or(self, tree: Tree) -> bool:
            return tree[0] or tree[1]
        def implies(self, tree: Tree) -> bool:
            return (not tree[0]) or tree[1]
        def equivalent(self, tree: Tree) -> bool:
            return ((not tree[0]) or tree[1]) and ((not tree[1]) or tree[0])

    return Evaluator().transform(tree)

# here we check that the user's answer is not the same as the prohibited formula
# we take into account that the user may have simply changed the operand order of the commutative "and", "or" operators
# and/or padded the prohibited formula with preceeding "not" operators that all cancel out
# and/or repeated the prohibited formula with "and"s/"or"s inbetween
def is_prohibited(user_tree: Tree, prohibited_tree: Tree) -> bool:
    class CheckProhibited(Transformer):
        def letter(self, tok: Token) -> str:
            return tok[0].value
        def brackets(self, tree: Tree) -> str:
            return tree[0]
        def not_letter(self, tok: Token) -> str:
            return "NOT" + tok[0].value
        def not_formula(self, tree: Tree) -> str:
            return "NOT" + tree[0]
        def _and(self, tree: Tree) -> str:
            if tree[0] < tree[1]:   # sort operand order based on alphabetical order, so user cannot simply swap operands
                return "AND(" + tree[0] + "," + tree[1] + ")"
            else:
                return "AND(" + tree[1] + "," + tree[0] + ")"
        def _or(self, tree: Tree) -> str:
            if tree[0] < tree[1]:
                return "OR(" + tree[0] + "," + tree[1] + ")"
            else:
                return "OR(" + tree[1] + "," + tree[0] + ")"
        def implies(self, tree: Tree) -> str:
            return "IMPLIES(" + tree[0] + "," + tree[1] + ")"
        def equivalent(self, tree: Tree) -> str:
            return "EQUIVALENT(" + tree[0] + "," + tree[1] + ")"
    
    prohibited_check = CheckProhibited().transform(prohibited_tree)

    class CheckProhibitedUser(CheckProhibited):
        def not_letter(self, tok: Token) -> str:
            t = tok[0].value
            if t[:3] == "NOT":  # cancel out "not"s to prevent user from padding prohibited formula with these
                return t[3:]
            return "NOT" + t
        def not_formula(self, tree: Tree) -> str:
            t = tree[0]
            if t[:3] == "NOT":
                return t[3:]
            return "NOT" + t
        def _and(self, tree: Tree) -> str:
            if tree[0] == prohibited_check and tree[1] == prohibited_check:  # prevent user from repeating prohibited formula with "and" inbetween
                return tree[0]
            if tree[0] < tree[1]:   # sort operand order based on alphabetical order, so user cannot simply swap operands
                return "AND(" + tree[0] + "," + tree[1] + ")"
            else:
                return "AND(" + tree[1] + "," + tree[0] + ")"
        def _or(self, tree: Tree) -> str:
            if tree[0] == prohibited_check and tree[1] == prohibited_check:  # prevent user from repeating prohibited formula with "or" inbetween
                return tree[0]
            if tree[0] < tree[1]:
                return "OR(" + tree[0] + "," + tree[1] + ")"
            else:
                return "OR(" + tree[1] + "," + tree[0] + ")"

    if CheckProhibitedUser().transform(user_tree) == prohibited_check:
        return True
    return False

def check_equivalent(f1_tree: str, f2_tree: str) -> bool:
    class GetLetters(Visitor):
        letters = set()
        def letter(self, tree: Tree):
            self.letters.add(tree.children[0].value)
        def not_letter(self, tree: Tree):
            self.letters.add(tree.children[0].value)

    f1_visitor = GetLetters()
    f2_visitor = GetLetters()
    f1_visitor.visit(f1_tree)
    f2_visitor.visit(f2_tree)

    if f1_visitor.letters != f2_visitor.letters:    # if f1 and f2 don't contain the same variable letters, they cannot be equivalent
        return False

    def test_valuation(valuation: Dict[str, bool], letters: List[str], i: int) -> bool:
        if evaluate_tree(f1_tree, valuation) != evaluate_tree(f2_tree, valuation):
            return False
        
        valuation_copy = valuation.copy()
        valuation_copy[letters[i]] = not valuation[letters[i]]   # negate truth value of letter i

        if evaluate_tree(f1_tree, valuation_copy) != evaluate_tree(f2_tree, valuation_copy):  # test with this different valuation
            return False

        if i == 0:  # tested all possible valuations
            return True

        return test_valuation(valuation, letters, i-1) and test_valuation(valuation_copy, letters, i-1)     # recursively test all possible valuations

    valuation = {}
    for l in f1_visitor.letters:
        valuation[l] = False
    letters = list(valuation.keys())

    return test_valuation(valuation, letters, len(valuation)-1)

def validate_answer(answer_formula: str, correct_formula: str, prohibited_formula: str, grammar: str) -> str:
    answer_parser = None
    correct_parser = None
    answer_tree  = None
    correct_tree = None

    has_prohibited = prohibited_formula != ""
    prohibited_tree = None

    if grammar == "prop":
        answer_parser = correct_parser = prop_parser
    elif grammar == "dnf":
        answer_parser = dnf_parser
        correct_parser = prop_parser
    else:
        answer_parser = correct_parser = bool_parser

    try:
        answer_tree  = answer_parser.parse(answer_formula)
        correct_tree = correct_parser.parse(correct_formula)
        if has_prohibited:
            prohibited_tree = answer_parser.parse(prohibited_formula)
    except LarkError:
        return "Parse error. Correct answer was " + correct_formula

    if has_prohibited and is_prohibited(answer_tree, prohibited_tree):
        return "Prohibited formula. Correct answer was " + correct_formula

    if check_equivalent(answer_tree, correct_tree):
        return "Correct"
    else:
        return "Incorrect. Correct answer was " + correct_formula

def gen_truth_table(f: str, letters: List[str], grammar: str):
    tree = None
    if grammar == "prop":
        tree = prop_parser.parse(f)
    else:
        tree = bool_parser.parse(f)
    
    truth_table = set()
    def evaluate(valuation: Dict[str, bool], i: int):
        truth_table.add((tuple(valuation.values()), evaluate_tree(tree, valuation)))

        valuation_copy = valuation.copy()
        valuation_copy[letters[i]] = not valuation[letters[i]]

        truth_table.add((tuple(valuation_copy.values()), evaluate_tree(tree, valuation_copy)))

        if i == 0:
            return

        evaluate(valuation, i-1)
        evaluate(valuation_copy, i-1)

    valuation = {}
    for l in letters:
        valuation[l] = False
    evaluate(valuation, len(letters)-1)

    table_str = "<table class ='table'><thead><tr>"
    for l in letters:
        table_str += "<th scope='col'>\\(" + l + "\\)</th>"
    table_str += "<th scope='col'>\\(?\\)</th></tr></thead><tbody>"
    for v in truth_table:
        table_str += "<tr>"
        for t in v[0]:
            table_str += "<td>" + ("\\(0\\)" if not t else "\\(1\\)") + "</td>"
        table_str += "<td>" + ("\\(0\\)" if not v[1] else "\\(1\\)") + "</td>"
        table_str += "</tr>"

    table_str += "</tbody></table>"
    return table_str

def translate_formula(formula: str, letters: List[str], grammar: str) -> str:
    phrases = [("it is dark", "it is night"), ("it is snowing", "it is cold"), ("it is late", "I am tired")]
    phrases_negative = [("it is not dark", "it is not night"), ("it is not snowing", "it is not cold"), ("it is not late", "I am not tired")]

    p = random.randint(0, len(phrases)-1)
    
    class Translator(Transformer):
        def letter(self, tok: Token) -> str:
            t = tok[0].value
            return phrases[p][letters.index(t)]
        def brackets(self, tree: Tree) -> str:
            return tree[0]
        def not_letter(self, tok: Token) -> str:
            t = tok[0].value
            return phrases_negative[p][letters.index(t)]
        def not_formula(self, tree: Tree) -> str:
            return "it is not that (" + tree[0] +")"
        def _and(self, tree: Tree) -> str:
            return "(" + tree[0] + ") and (" + tree[1] +")"
        def _or(self, tree: Tree) -> str:
            return "(" + tree[0] + ") or (" + tree[1] +")"
        def implies(self, tree: Tree) -> str:
            return "if (" + tree[0] + "), then (" + tree[1] + ")"
        def equivalent(self, tree: Tree) -> str:
            return "(" + tree[0] + ") if and only if (" + tree[1] + ")"

    tree = None
    if grammar == "prop":
        tree = prop_parser.parse(formula)
    else:
        tree = bool_parser.parse(formula)

    sentence = Translator().transform(tree)
    
    meanings = [(l, phrases[p][letters.index(l)]) for l in letters]
    meanings_str = ""
    for i in range(len(meanings)):
        meanings_str += "\\(" + meanings[i][0] + "\\)" + " = " + meanings[i][1]
        if i != len(meanings)-1:
            meanings_str += ", "
    
    return "Let " + meanings_str + ". " + sentence

def generate_question() -> Tuple[str, str, str, str, str]:
    prop_letters = ["p", "q", "r", "s", "t"]
    bool_letters = ["a", "b", "c", "d", "e"]

    def gen_prop(formula: str, length: int) -> Tuple[str, List[str]]:    # here "length" is the number of derivations we have performed so far
        if length <= 0:
            formula = formula.replace("F", "L")     # we will now replace all non-terminals with letters
            max_letters = random.randint(1, len(prop_letters))
            letters = set()
            while "L" in formula:
                l = prop_letters[random.randint(0, max_letters-1)]
                formula = formula.replace("L", l, 1)
                letters.add(l)
            return (formula, list(letters))

        derivations = ["-L", "F ^ F", "F < F", "F -> F", "F <-> F", "(F ^ F)", "(F < F)", "(F -> F)", "(F <-> F)", "-(F ^ F)", "-(F < F)", "-(F -> F)", "-(F <-> F)"]
        d = random.sample(derivations, 1)
        formula = formula.replace("F", d[0], 1)

        return gen_prop(formula, length-1)
    
    def gen_bool(formula: str, length: int) -> Tuple[str, List[str]]:
        if length <= 0:
            formula = formula.replace("F", "L")     # we will now replace all non-terminals with letters
            max_letters = random.randint(1, len(bool_letters))
            letters = set()
            while "L" in formula:
                l = bool_letters[random.randint(0, max_letters-1)]
                formula = formula.replace("L", l, 1)
                letters.add(l)
            return (formula, list(letters))

        derivations = ["-L", "F . F", "F + F", "(F . F)", "(F + F)", "-(F . F)", "-(F + F)"]
        d = random.sample(derivations, 1)
        formula = formula.replace("F", d[0], 1)

        return gen_bool(formula, length-1)

    grammar = ""
    formula = ""
    prohibited_formula = ""
    prompt = ""
    input_method = ""

    question_type = random.randint(0, 4)
    if question_type == 0:
        grammar = "prop"
        gen = gen_prop("F", 2)
        formula = gen[0]
        letters = gen[1]
        
        if len(letters) == 2:
            prompt = "Translate the following sentence into a propositional logic formula: " + translate_formula(formula, letters, grammar)
        else:
            prohibited_formula = formula
            prompt = "Give an equivalent propositional logic formula to \\(" + formula.replace("<->", "\\longleftrightarrow").replace("->", "\\rightarrow").replace("^", "\\land").replace("-", "\\neg ").replace("<", "\\lor") + "\\)"
            input_method = "Text"   # can't be blocks, since blocks would form prohibited formula

    elif question_type == 1:
        grammar = "bool"
        gen = gen_bool("F", 2)
        formula = gen[0]
        letters = gen[1]
        
        if len(letters) == 2:
            prompt = "Translate the following sentence into a boolean algebra formula: " + translate_formula(formula, letters, grammar)
        else:
            prohibited_formula = formula
            prompt = "Give an equivalent boolean algebra formula to \\(" + formula.replace(".", "\\cdot") + "\\)"
            input_method = "Text"

    elif question_type == 2:
        grammar = "prop"
        gen = gen_prop("F", 2)
        formula = gen[0]
        table = gen_truth_table(formula, gen[1], grammar)
        prompt = "Give a propositional logic formula for the following truth table:\n" + table

    elif question_type == 3:
        grammar = "bool"
        gen = gen_bool("F", 2)
        formula = gen[0]
        table = gen_truth_table(formula, gen[1], grammar)
        prompt = "Give a boolean algebra formula for the following truth table:\n" + table
        
    elif question_type == 4:
        grammar = "dnf"
        formula = gen_prop("F", 2)[0]
        prompt = "Give the following propositional logic formula in DNF: \\(" + formula.replace("<->", "\\longleftrightarrow").replace("->", "\\rightarrow").replace("^", "\\land").replace("-", "\\neg ").replace("<", "\\lor") + "\\)"
        input_method = "Text"

    if input_method == "":
        if random.randint(0, 1) == 0:
            input_method = "Text"
        else:
            input_method = "Blocks"

    return (grammar, formula, prohibited_formula, prompt, input_method)


# Prevents this test code breaking things when logic engine used as a library
if __name__ == '__main__':
    question = generate_question()
    print(question[3])

    answer = input()
    print(validate_answer(answer, question[1], question[2], question[0]))
