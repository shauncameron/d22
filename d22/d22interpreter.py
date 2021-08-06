from d22.d22error import d22Error, d22Traceback
from d22.d22lexer import *
from d22.d22symbol import *
from random import randint, choice
from d22.d22ast import *
from typing import Union

#  Need to re-do symbol system

BOOLOPMAPPING = {
    LESSTHAN: '__lessthan22__',
    MORETHAN: '__morethan22__',
    LESSTHANEQUALS: '__lessthaneq22__',
    MORETHANEQUALS: '__morehtaneq22__',
    COMPAREEQUALS: '__eq22__',
    NOTEQUALS: '__neq22__',
    AMPERSAND: '__and22__',
    PIPE: '__or22__',
}

MATHOPMAPPING = {
    PLUS: '__plus22__',
    MINUS: '__minus22__',
    MULTIPLY: '__mul22__',
    DIVIDE: '__div22__',
    EXPONENT: '__pow22__',
    FLOOR: '__floor22__'
}


#  Object will be a symbol type
#  Method mapping for number type symbols
#  Math type operations

class d22Interpreter:
    def __init__(self, parsing, text, context):
        self.parsing = parsing
        self.text = text
        self.context = context

        self.lastevaluatednonboolean = None
        self.lastexpression = parsing

    def visit(self, node) -> (d22Symbol, Union[d22Error, None]):
        try:
            visitor = getattr(self, f'visit{type(node).__name__}', lambda n: self.error(n.token.traceback, f'(INternal) Interpreter cannot handle current node: {type(node).__name__}'))

            returned = visitor(node)
            if returned is None or len(returned) != 2:
                return self.error(node.token.traceback, f'Visiting node "{type(node).__name__}" had no proper handling')

            result, error = returned
            if error: return None, error

            if node.evaluation is None:
                node.evaluation = result

            return result, None
        except RecursionError:
            return self.error(node.token.traceback, f'Maximum recursion depth (998) exceeded when evaluating: "{node}"')

    def error(self, traceback, message):
        return None, d22Error(traceback, message)

    def visitUOPExpressionSequence(self, node):
        expressions = []

        for value in node.value:
            result, error = self.visit(value)
            if error: return None, error

            expressions.append(result)

        return d22SequenceSymbol(expressions, node.token), None

    def visitBinaryOperation(self, node):
        left, error = self.visit(node.left)
        if error: return None, error

        right, error = self.visit(node.right)
        if error: return None, error

        if node.operator.grammar in MATHOPMAPPING:
            mappedfunc = MATHOPMAPPING[node.operator.grammar]

            result, error = self.d22_meth_map_num(node.token.traceback, left, mappedfunc, node, self, right, node=node)
            if error: return None, error

            self.lastevaluatednonboolean = result
            node.lefteval = f'{node.left.evaluation}'
            node.righteval = f'{node.right.evaluation}'

            return result, None

        else:
            return self.error(node.token.traceback, f'(Internal) Could not map passed operator {node.operator}')

    def visitBinaryBooleanOperation(self, node):
        left, error = self.visit(node.left)
        if error: return None, error

        right, error = self.visit(node.right)
        if error: return None, error

        if node.operator.grammar in BOOLOPMAPPING:
            mappedfunc = BOOLOPMAPPING[node.operator.grammar]

            result, error = self.d22_meth_map_num(node.token.traceback, left, mappedfunc, node, self, right, node=node)
            if error: return None, error

            node.lefteval = f'{node.left.evaluation}'
            node.righteval = f'{node.right.evaluation}'

            return result, None

        else:
            return self.error(node.token.traceback, f'(Internal) Could not map passed operator {node.operator}')

    def visitUOPFrozen(self, node):
        result, error = self.visit(node.value)
        if error: return None, error

        return d22FrozenSymbol(result, node.token), None

    def visitUOPAssign(self, node):
        result, error = self.visit(node.value)
        if error: return None, error

        self.context(node.identifier, result)

        return result, None

    def visitUOPReference(self, node):
        if member := self.context(node.value):
            result, error = member.value(node, self)
            if error: return None, error

            return result, None
        else:
            return self.error(node.token.traceback, f'There is no such member as "{node.value}" in current context')

    def visitUOPExpressionChain(self, node):
        result = None

        ifcon, error = self.visit(node.ifcon)
        if error: return None, error

        tb, error = ifcon.bool()
        if error: return None, error
        if tb:
            result, error = self.visit(node.ifthen)
            if error: return None, error

            node.evaluation = f'? {ifcon} : {result}'

            return result, None

        else:
            node.evaluation = f'~~{ifcon}~~'

        if len(node.elifs):

            for elifcon in node.elifs:
                tb, error = elifcon.bool()
                if error: return None, error
                if tb:
                    result, error = self.visit(node.ifthen)
                    if error: return None, error
                else:
                    node.evaluation += f' ~~{elifcon}~~'

        if result is None:
            result, error = self.visit(node.elsethen)
            if error: return None, error

            node.evaluation += f' ?? {result}'

        return result, None

    def visitUOPNot(self, node):
        result, error = self.visit(node.value)
        if error: return None, error

        tf, error = self.d22_bool(node.token.traceback, result, node=node)
        if error: return None, error

        return (d22Symbol('false', node.token, False), None) if tf else (d22Symbol('true', node.token, True), None)

    def visitUOPNegative(self, node):
        result, error = self.visit(node.value)
        if error: return None, error

        result, error = result.__negative22__(node, self)
        if error: return None, error

        return result, None

    def visitUOPHighest(self, node):
        result, error = self.visit(node.value)
        if error: return None, error

        result, error = result.__highest22__(node, self, node.amount)
        if error: return None, error

        return result, None

    def visitUOPLowest(self, node):
        result, error = self.visit(node.value)
        if error: return None, error

        result, error = result.__lowest22__(node, self, node.amount)
        if error: return None, error

        return result, None

    def visitUOPRandom(self, node):
        result, error = self.visit(node.value)
        if error: return None, error

        result, error = result.__random22__(node, self, int(float(node.amount)))
        if error: return None, error

        return result, None

    def visitUOPDrop(self, node):
        pass

    def visitUOPDiceRoll(self, node):
        if node.amount:
            rolls = []
            for _ in range(int(float(node.amount))):
                rolls.append(d22NumberSymbol(randint(1, int(float(node.value))), node.token))
            return d22SequenceSymbol(rolls, node.token), None
        else:
            return d22NumberSymbol(randint(1, int(float(node.value))), node.token), None

    def visitUOPNumber(self, node):
        return d22NumberSymbol(int(float(node.value)), node.token), None

    def visitUOPLambda(self, node):
        return d22LambdaSymbol(node.value, node.token, False), None

    def visitUOPCaret(self, node):
        if leval := self.lastexpression:
            result, error = self.visit(leval)  # This is in it's AST form
            if error: return None, error

            return result, None
        else:
            return None, d22Error(node.token.traceback,
                                  'In this context, there exists no evaluated lambda-type expression')

    def visitUOPDot(self, node):
        if leval := self.lastevaluatednonboolean:
            return leval, None  # This is already interpreted
        else:
            return None, d22Error(node.token.traceback,
                                  'In this context, there exists no evaluated non-boolean expression')

    def visitUOPiPositive(self, node):
        return d22IneffectualSymbol('~', node.token, True), None

    def visitUOPiNegative(self, node):
        return d22IneffectualSymbol('~~', node.token, False), None

    def visitAnnotated(self, node):
        """
        :param node:
            :param node.value: interpreted
            :param node.annotation: annotation applied to interpretation
        :return:
        """
        result, error = self.visit(node.value)
        if error: return None, error

        result.setannotation(self, node.annotation)

        return result, None

    def d22_meth_map_num(self, tb: d22Traceback, obj: d22Symbol, method: str, *args, node=None, **kwargs):
        """
        :param tb: traceback for errors
        :param node:  ?.value() requires node parameter
        :param symbol obj: Symbol Type object to perform getting the value -> number on
        :param str method: Name of the method as a string
        :param args: Arguments passed into method of number
        :param kwargs: Keyword arguments passed into method of number
        :return: Returned values from gotten method
        """
        if node is None:
            print(tb, obj, method, args, kwargs)
            quit()

        number, error = obj.value(node, self)  # This accounts for lambda type objects
        if error: return None, error

        method = getattr(number, method, None)
        if method is None:
            return None, d22Error(tb,
                                  f'(Internal) Failed to retrieve method by name "{method}" inside of number "{number}"')

        result = method(*args, **kwargs)

        return result

    def d22_bool(self, tb: d22Traceback, obj: d22Symbol, node=None):
        """
        :param tb: traceback for errors
        :param node: ?.value() requires node parameter
        :param symbol obj: Object to get boolean of
        :return: (python) True or False
        """
        value, error = obj.value(node, self)
        if error: return None, error

        tf, error = value.bool()
        if error: return None, error

        if tf in (True, False):
            return tf, None

        else:
            return None, d22Error(tb, f'(Internal) ?.bool() of "{value}" did not return python True or python False')
