from d22.d22error import d22Traceback, d22Error
from re import match as rematch, sub as resub


class d22GrammarMatch:
    def __init__(self, pattern=None, parent=None):
        self.pattern = pattern

        self.parent = id(self) if parent is None else parent
        self.parent: d22GrammarMatch

    def __call__(self, pattern=None):
        return d22GrammarMatch(pattern, self)

    def childof(self, other) -> bool:
        if type(other) is d22GrammarMatch:
            if other is self.parent:
                return True
            else:
                return False
        else:
            return False

    def parentof(self, other) -> bool:
        if type(other) is d22GrammarMatch:
            if other.parent is self:
                return True
            else:
                return False
        else:
            return False

    def siblingof(self, other) -> bool:
        if type(other) is d22GrammarMatch:
            if other.parent is self.parent:
                return True
            else:
                return False
        else:
            return False

class d22Token:
    def __repr__(self):
        return f'"{self.value}"'

    def __init__(self, value, grammar: d22GrammarMatch, traceback: d22Traceback):
        self.value = value

        self.grammar = grammar
        self.parentof = self.grammar.parentof
        self.childof = self.grammar.childof
        self.siblingof = self.grammar.siblingof

        self.traceback = traceback

    def spawnof(self, other):
        if self.grammar is other:
            return True
        else:
            return False

EXPRESSION = d22GrammarMatch()
SELECTOR = d22GrammarMatch()
OPERATOR = d22GrammarMatch()
BOOLTERM = OPERATOR()
TERM5 = OPERATOR()
TERM4 = OPERATOR()
TERM3 = OPERATOR()
TERM2 = OPERATOR()
TERM1 = OPERATOR()
FACTOR = d22GrammarMatch()
OTHER = d22GrammarMatch()

GRAMMAR = (
    LPARENTHESES := FACTOR(r'^\('),
    RPARENTHESES := FACTOR(r'^\)'),
    LAMBDA := FACTOR(r'^\$'),
    DOT := FACTOR('^\.'),
    CARET := FACTOR('^\^'),
    DICEROLL := FACTOR(r'^([0-9]*)d([0-9]+)'),
    NUMBER := FACTOR(r'^-?(?:[0-9]*\.?)?[0-9]+'),
    LASTRESULT := FACTOR(r'^\.'),
    IDENTIFIER := FACTOR(r'^_[a-zA-Z_]+[a-zA-Z0-9_]*'),
    NEGATIVETILDE := FACTOR(r'^~~'),
    POSITIVETILDE := FACTOR(r'^~'),

    HASHTAG := EXPRESSION(r'^#'),
    ASSIGNEQUALS := EXPRESSION(r'^='),
    THEN := EXPRESSION(r'^:'),
    ELSE := EXPRESSION(r'^\?\?'),
    IF := EXPRESSION(r'^\?'),
    NOT := EXPRESSION(r'^!'),
    DROP := EXPRESSION(r'^d'),
    NEGATIVE := EXPRESSION(r'^-'),

    HIGHEST := SELECTOR(r'^h([0-9]*)'),
    LOWEST := SELECTOR(r'^l([0-9]*)'),
    RANDOM := SELECTOR(r'^r([0-9]*)'),

    LESSTHANEQUALS := BOOLTERM(r'^<='),
    MORETHANEQUALS := BOOLTERM(r'^>='),
    LESSTHAN := BOOLTERM(r'^<'),
    MORETHAN := BOOLTERM(r'^>'),
    COMPAREEQUALS := BOOLTERM(r'^=='),
    NOTEQUALS := BOOLTERM(r'^!='),
    AMPERSAND := BOOLTERM(r'^&'),
    PIPE := BOOLTERM(r'^\|'),

    PLUS := TERM5(r'^\+'),
    MINUS := TERM5(r'^-'),

    EXPONENT := TERM3(r'^\*\*'),
    FLOOR := TERM3(r'^\/\/'),

    MULTIPLY := TERM4(r'^\*'),
    DIVIDE := TERM4(r'^\/'),

    COMMA := OTHER(r'^,'),

    ANNOTATION := OTHER(r'^\[(.*)\]'),
    FACTORASSIGN := TERM1(r'^:='),

    WHITESPACE := OTHER(r'^\s+'),
)

def lex(string: str):
    text = string
    tokens = []

    col = 0
    last = ''
    while len(string):
        matched = False
        if last == string:
            break

        for grammar in GRAMMAR:
            if mo := rematch(grammar.pattern, string):
                value = mo.groups() if len(mo.groups()) else mo.group()
                tokens.append(d22Token(value, grammar, d22Traceback(text, col)))

                olen = len(string)
                string = resub(grammar.pattern, '', string)
                col += olen - len(string)

                matched = True
                break

        if not matched:
            return None, d22Error(d22Traceback(text, col), 'Could not matched current onward string to a token value')

    return [t for t in tokens if not t.spawnof(WHITESPACE)], None
