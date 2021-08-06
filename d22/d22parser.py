from d22.d22error import d22Error, d22Traceback
from d22.d22lexer import *
from d22.d22ast import *

SOF = d22GrammarMatch()
EOF = d22GrammarMatch()


class d22Parser:
    def __init__(self, tokens, text):
        self.tokens = tokens
        self.text = text

        self.token = d22Token('', SOF, d22Traceback(self.text, 0))  # Token of start of text
        self.prevtoken = d22Token('', SOF, d22Traceback(self.text, 0))  # Last token advanced
        self.token_index = -1

        self.advance()

    def error(self, message):
        return None, d22Error(self.token.traceback, message)

    def advance(self, amount=1):
        if len(self.tokens):
            if self.token_index + amount < len(self.tokens):
                self.prevtoken = self.token
                self.token_index += amount
                self.token = self.tokens[self.token_index]
            else:
                self.prevtoken = self.token
                self.token = d22Token('$', EOF, d22Traceback(self.text, len(self.text) - 1))
        else:
            self.token = d22Token('$', EOF, d22Traceback(self.text, len(self.text) - 1))

    def look(self, amount=1) -> d22Token:
        if len(self.tokens):
            if self.token_index + amount < len(self.tokens):
                return self.tokens[self.token_index + amount]
            else:
                return d22Token('$', EOF, d22Traceback(self.text, len(self.text) - 1))
        else:
            return d22Token('$', EOF, d22Traceback(self.text, len(self.text) - 1))

    def parse(self):
        result, error = self.expression()
        if error: return None, error

        if not self.token.spawnof(EOF):
            return self.error('Expected the end of the expression')

        return result, None

    def expression(self):
        token = self.token
        result, error = self.microexpression()
        if error: return None, error

        if self.token.spawnof(COMMA):
            expressions = [result]

            while self.token.spawnof(COMMA):
                self.advance()

                expression, error = self.microexpression()
                if error: return None, error

                expressions.append(expression)
            return UOPExpressionSequence(expressions, token), None
        else:
            return result, None

    def microexpression(self):
        if self.token.spawnof(IDENTIFIER):
            identifier = self.token
            if self.look().spawnof(ASSIGNEQUALS):
                self.advance(2)  # To assign, Past assign

                expression, error = self.expression()
                if error: return None, error

                return UOPAssign(identifier.value, expression, identifier), None

            else:
                result, error = self.boolterm()  # Not assigning, so skip
                if error: return None, error

                return result, None

        elif self.token.spawnof(IF):
            iftoken = self.token
            self.advance()

            ifcondition, error = self.expression()
            if error: return None, error

            if self.token.spawnof(THEN):
                self.advance()

                ifthen, error = self.expression()
                if error: return None, error

                elifs = []
                while self.token.spawnof(IF):
                    self.advance()

                    elifcondition, error = self.expression()
                    if error: return None, error

                    if self.token.spawnof(THEN):
                        self.advance()

                        elifthen, error = self.expression()
                        if error: return None, error

                        elifs.append((elifcondition, elifthen))
                    else:
                        return self.error('Expected ":" THEN to follow an elif expression condition')

                if self.token.spawnof(ELSE):
                    self.advance()

                    elsethen, error = self.expression()
                    if error: return None, error

                    return UOPExpressionChain(ifcondition, ifthen, elifs, elsethen, iftoken), None

                else:
                    return self.error('Expected "??" ELSE to follow an if/elif expression ":" THEN. (An if type expression chain must result in some sort of value result)')

            else:
                return self.error('Expected ":" THEN to follow an if expression condition')

        elif self.token.spawnof(DROP):
            droptoken = self.token
            self.advance()

            if self.token.spawnof(THEN):
                self.advance()

            expression, error = self.expression()
            if error: return None, error

            return UOPDrop(expression, droptoken)

        elif self.token.spawnof(NEGATIVE):
            negtoken = self.token
            self.advance()

            expression, error = self.expression()
            if error: return None, error

            return UOPNegative(expression, negtoken), None

        else:
            result, error = self.boolterm()
            if error: return None, error

            return result, None

    def boolterm(self):
        left, error = self.term5()
        if error: return None, error

        while self.token.childof(BOOLTERM):
            op = self.token
            self.advance()

            right, error = self.term5()
            if error: return None, error

            left = BinaryBooleanOperation(left=left, operator=op, right=right, token=op)

        return left, None

    def term5(self):
        left, error = self.term4()
        if error: return None, error

        while self.token.childof(TERM5):
            op = self.token
            self.advance()

            right, error = self.term4()
            if error: return None, error

            left = BinaryOperation(left=left, operator=op, right=right, token=op)

        return left, None

    def term4(self):
        left, error = self.term3()
        if error: return None, error

        while self.token.childof(TERM4):
            op = self.token
            self.advance()

            right, error = self.term3()
            if error: return None, error

            left = BinaryOperation(left=left, operator=op, right=right, token=op)

        return left, None

    def term3(self):
        left, error = self.term2()
        if error: return None, error

        while self.token.childof(TERM3):
            op = self.token
            self.advance()

            right, error = self.term2()
            if error: return None, error

            left = BinaryOperation(left=left, operator=op, right=right, token=op)

        return left, None

    def term2(self):
        left, error = self.term1()
        if error: return None, error

        while self.token.childof(TERM2):
            op = self.token
            self.advance()

            right, error = self.term1()
            if error: return None, error

            left = BinaryOperation(left=left, operator=op, right=right, token=op)

        return left, None

    def term1(self):
        left, error = self.factor()
        if error: return None, error

        while self.token.spawnof(TERM1):
            op = self.token
            self.advance()

            right, error = self.factor()
            if error: return None, error

            left = BinaryOperation(left=left, operator=op, right=right, token=op)

        return left, None

    def factor(self):
        if self.token.spawnof(HIGHEST):
            token = self.token
            self.advance()

            if self.token.spawnof(THEN):
                self.advance()

            expression, error = self.expression()
            if error: return None, error

            left = UOPHighest(token.value[0], expression, token)

        elif self.token.spawnof(LOWEST):
            token = self.token
            self.advance()

            if self.token.spawnof(THEN):
                self.advance()

            expression, error = self.expression()
            if error: return None, error

            left = UOPLowest(token.value[0], expression, token)

        elif self.token.spawnof(RANDOM):
            token = self.token
            self.advance()

            if self.token.spawnof(THEN):
                self.advance()

            expression, error = self.expression()
            if error: return None, error

            left = UOPRandom(token.value[0], expression, token)

        elif self.token.spawnof(LPARENTHESES):
            self.advance()

            expression, error = self.expression()
            if error: return None, error

            if self.token.spawnof(RPARENTHESES):
                self.advance()

                left = expression
            else:
                return self.error('Expected closing parentheses')

        elif self.token.spawnof(DICEROLL):
            token = self.token
            self.advance()

            left = UOPDiceRoll(token.value[0], token.value[1], token)

        elif self.token.spawnof(NUMBER):
            number = self.token
            self.advance()

            left = UOPNumber(number.value, number)

        elif self.token.spawnof(CARET):
            caret = self.token
            self.advance()

            left = UOPCaret(caret)

        elif self.token.spawnof(LAMBDA):
            ld = self.token
            self.advance()

            factor, error = self.factor()  # Lambda takes a single expression, but that includes "("
            if error: return None, error

            left = UOPLambda(factor, ld)

        elif self.token.spawnof(NOT):
            nottoken = self.token
            self.advance()

            expression, error = self.expression()
            if error: return None, error

            return UOPNot(expression, nottoken), None

        elif self.token.spawnof(HASHTAG):
            frozen = self.token
            self.advance()

            factor, error = self.factor()  # Lambda takes a single expression, but that includes "("
            if error: return None, error

            left = UOPFrozen(factor, frozen)

        elif self.token.spawnof(DOT):
            dot = self.token
            self.advance()

            left = UOPDot(dot)

        elif self.token.spawnof(POSITIVETILDE):
            token = self.token
            self.advance()

            left = UOPiPositive(token)

        elif self.token.spawnof(NEGATIVETILDE):
            token = self.token
            self.advance()

            left = UOPiNegative(token)

        elif self.token.spawnof(IDENTIFIER):
            identifier = self.token
            self.advance()

            left = UOPReference(identifier.value, identifier)

        else:
            return self.error('Expected FACTOR')

        if self.token.spawnof(ANNOTATION):
            annotation = self.token
            self.advance()

            return Annotated(left, annotation, annotation),

        elif self.token.spawnof(IF):
            token = self.token
            self.advance()

            ifcon, error = self.expression()
            if error: return None, error

            if self.token.spawnof(ELSE):
                self.advance()
                elsethen, error = self.expression()
                if error: return None, error

                return UOPExpressionChain(ifcon, left, [], elsethen, token), None

            else:

                return self.error('Expected "??" ELSE to follow an if factor-time expression')

        else:

            return left, None