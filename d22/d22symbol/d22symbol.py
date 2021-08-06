from random import choice, shuffle, randint

from d22.d22error import *
from d22.d22lexer import d22Token
from d22.d22ast import *
from typing import Union

#  A method must return a symbol (with the exception of true or false


class d22Symbol:
    def __repr__(self):
        return f'<Type: {self._value}>'

    def __init__(self, value, token: d22Token, booltype: bool = True, annotation: str = None):
        self._value = value
        self.token = token
        self._bool = booltype
        self._annotation = annotation

        self.value = lambda n, i: (self, None)
        self.bool = lambda: (self._bool, None)
        self.number = lambda n, i: (None, d22Error(self.token.traceback, f'{self} does not support number conversion'))
        self.annotation = lambda i: (None, self._annotation)
        self.setannotation = lambda i, a: setattr(self, '_annotation', a)

    def __negative22__(self, node, interpreter):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "negative()" on "{self}"')

    def __highest22__(self, node, interpreter, amount):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "highest()" on "{self}"')

    def __lowest22__(self, node, interpreter, amount):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "lowest()" on "{self}"')

    def __random22__(self, node, interpreter, amount):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "random()" on "{self}"')

    def __drop22__(self, node, interpreter, amount):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "drop()" on "{self}"')

    def __lessthan22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__lessthan22__" on "{self}"')

    def __morethan22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__morethan22__" on "{self}"')

    def __lessthaneq22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__lessthaneq22__" on "{self}"')

    def __morehtaneq22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__morehtaneq22__" on "{self}"')

    def __eq22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__eq22__" on "{self}"')

    def __neq22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__neq22__" on "{self}"')

    def __and22__(self, node, interpreter, other):
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.bool()
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.bool()
            if error: return None, error

            return d22Symbol('true', node.token, True) if left and right else d22Symbol('false', node.token,
                                                                                          False), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__and22__" operation')

    def __or22__(self, node, interpreter, other):
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.bool()
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.bool()
            if error: return None, error

            return d22Symbol('true', node.token, True) if left or right else d22Symbol('false', node.token, False), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__and22__" operation')

    def __plus22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__plus22__" on "{self}"')

    def __minus22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__minus22__" on "{self}"')

    def __mul22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__mul22__" on "{self}"')

    def __div22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__div22__" on "{self}"')

    def __pow22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__pow22__" on "{self}"')

    def __floor22__(self, node, interpreter, other):
        return None, d22Error(node.token.traceback, f'Unsupported mapped operation of "__floor22__" on "{self}"')

    def __d22repr__(self):
        return f'<Type: {self._value}>'

    def __d22display__(self):
        return f'{self._value}'


class d22LambdaSymbol(d22Symbol):
    def __repr__(self):
        return f'<Lambda: $({self._value})>'

    def __init__(self, value: AST, token: d22Token, booltype: bool = True, annotation: str = None):
        super().__init__(value, token, booltype, annotation)

        def value(node, interpreter):
            og = interpreter.lastexpression
            interpreter.lastexpression = self._value

            result, error = interpreter.visit(self._value)
            if error: return None, error

            interpreter.lastexpression = og

            return result, None
        self.value = value

    def __d22repr__(self):
        return f'<Lambda: ${self._value.__22_plain__()}>'

    def __d22display__(self):
        return f'$({self._value.__22_plain__()})'


class d22NumberSymbol(d22Symbol):
    def __repr__(self):
        return f'<Number: {self._value}>'

    def __init__(self, value: Union[int, float], token: d22Token, booltype: bool = True, annotation: str = None):
        super().__init__(int(float(value)) if type(value) not in (int, float) else value, token, booltype, annotation)
        self.number = lambda n, i: (self._value, None)

    def value(self, node, interpreter):
        result, error = interpreter.visit(self._value)
        if error: return None, error

        print(result)

        return result, None

    def __d22repr__(self):
        return f'<Number: {self._value}>'

    def __d22display__(self):
        return f'{self._value}'

    def __negative22__(self, node, interpreter):
        return d22NumberSymbol(-self._value, node.token), None

    def __plus22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return self, None
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.number(node, interpreter)
            if error: return None, error

            return d22NumberSymbol(left + right, node.token), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__plus22__" operation')

    def __minus22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return self, None
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.number(node, interpreter)
            if error: return None, error

            return d22NumberSymbol(left - right, node.token), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__minus22__" operation')

    def __mul22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return self, None
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.number(node, interpreter)
            if error: return None, error

            return d22NumberSymbol(left * right, node.token), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__mul22__" operation')

    def __div22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return self, None
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.number(node, interpreter)
            if error: return None, error

            if not right == 0:
                return d22NumberSymbol(left / right, node.token), None
            else:
                return None, d22Error(node.token.traceback, 'Cannot divide by Zero')
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__div22__" operation')

    def __pow22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return self, None
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.number(node, interpreter)
            if error: return None, error

            return d22NumberSymbol(left ** right, node.token), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__pow22__" operation')

    def __floor22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return self, None
        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = left.number(node, interpreter)
            if error: return None, error

            if not right == 0:
                return d22NumberSymbol(left // right, node.token), None
            else:
                return None, d22Error(node.token.traceback, 'Cannot divide by Zero')

        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__floor22__" operation')

    def __lessthan22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return other.bool()

        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = self.number(node, interpreter)
            if error: return None, error

            return d22Symbol('true', node.token, True) if left < right else d22Symbol('false', node.token, False), None
        else:
            return None, d22Error(node.token.traceback,
                                  'Unacceptable right operand given for "__lessthan22__" operation')

    def __morethan22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return other.bool()

        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = self.number(node, interpreter)
            if error: return None, error

            return d22Symbol('true', node.token, True) if left > right else d22Symbol('false', node.token, False), None
        else:
            return None, d22Error(node.token.traceback,
                                  'Unacceptable right operand given for "__morethan22__" operation')

    def __lessthaneq22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return other.bool()

        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = self.number(node, interpreter)
            if error: return None, error

            return d22Symbol('true', node.token, True) if left <= right else d22Symbol('false', node.token, False), None
        else:
            return None, d22Error(node.token.traceback,
                                  'Unacceptable right operand given for "__lessthaneq22__" operation')

    def __morehtaneq22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return other.bool()

        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = self.number(node, interpreter)
            if error: return None, error

            return d22Symbol('true', node.token, True) if left >= right else d22Symbol('false', node.token, False), None
        else:
            return None, d22Error(node.token.traceback,
                                  'Unacceptable right operand given for "__morehtaneq22__" operation')

    def __eq22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return other.bool()

        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = self.number(node, interpreter)
            if error: return None, error

            return d22Symbol('true', node.token, True) if left == right else d22Symbol('false', node.token, False), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__eq22__" operation')

    def __neq22__(self, node, interpreter, other: d22Symbol):
        if type(other) == d22IneffectualSymbol:
            return other.bool()

        if isinstance(other, d22Symbol):
            right, error = other.value(node, interpreter)
            if error: return None, error
            right, error = right.number(node, interpreter)
            if error: return None, error

            left, error = self.value(node, interpreter)
            if error: return None, error
            left, error = self.number(node, interpreter)
            if error: return None, error

            return d22Symbol('true', node.token, True) if left != right else d22Symbol('false', node.token, False), None
        else:
            return None, d22Error(node.token.traceback, 'Unacceptable right operand given for "__neq22__" operation')


class d22SequenceSymbol(d22NumberSymbol):
    def __repr__(self):
        return f'<Sequence: ({", ".join([f"{x}" for x in self._value])})>'

    def __init__(self, value: Union[tuple, list], token: d22Token, booltype: bool = True, annotation: str = None):
        super().__init__(0, token, booltype, annotation)
        self._value = value
        self.number = lambda n, i: (None, d22Error(self.token.traceback, f'{self} does not support number conversion'))

        def value(node, interpreter):
            if len(self._value):
                left = self._value[0]
                for right in tuple(self._value[1:]):
                    left, error = interpreter.d22_meth_map_num(node.token.traceback, left, '__plus22__', node, interpreter, right, node=node)
                    if error: return None, error
                return left, None
            else:
                return d22NumberSymbol(0, node.token), None

        self.value = lambda n, i: value(n, i)

    def __d22repr__(self):
        return f'<Sequence: ({", ".join([f"{x}" for x in self._value])})>'

    def __d22display__(self):
        return ", ".join([f"{x.__d22display__()}" for x in self._value])

    def __random22__(self, node, interpreter, amount):
        if amount is None:
            amount = 1
        else:
            amount = int(float(amount))

        if amount > 0:
            vals = []
            randomize = self._value[:]
            shuffle(randomize)
            for _ in range(amount):
                if _ >= len(randomize):
                    break
                vals.append(randomize[_])
            return d22SequenceSymbol(vals, node.token), None
        else:
            return None, interpreter.error(node.token.traceback, f'random() amount must be above 0, not "{amount}"')

    def __highest22__(self, node, interpreter, amount):
        if amount is None or amount == '':
            amount = 1
        else:
            amount = int(float(amount))

        if amount > 0:
            highest_numbers = []
            values = self._value[:]

            for _ in range(amount):
                if _ >= len(values):
                    break

                highest = d22NumberSymbol(float('-inf'), node.token)
                for each in values:
                    result, error = interpreter.d22_meth_map_num(node.token.traceback, each, '__morethan22__', node,
                                                                 interpreter, highest, node=node)
                    if error: return None, error

                    tb, error = result.bool()
                    if error: return None, error
                    if tb:
                        highest = each
                highest_numbers.append(highest)
                values.remove(highest)

            return d22SequenceSymbol(highest_numbers, node.token), None
        else:
            return None, interpreter.error(node.token.traceback, f'random() amount must be above 0, not "{amount}"')

    def __lowest22__(self, node, interpreter, amount):
        if amount is None or amount == '':
            amount = 1
        else:
            amount = int(float(amount))

        if amount > 0:
            lowest_numbers = []
            values = self._value[:]

            for _ in range(amount):
                if _ >= len(values):
                    break

                lowest = d22NumberSymbol(float('inf'), node.token)
                for each in values:
                    result, error = interpreter.d22_meth_map_num(node.token.traceback, each, '__lessthan22__', node,
                                                                 interpreter, lowest, node=node)
                    if error: return None, error

                    tb, error = result.bool()
                    if error: return None, error
                    if tb:
                        lowest = each
                lowest_numbers.append(lowest)
                values.remove(lowest)

            return d22SequenceSymbol(lowest_numbers, node.token), None
        else:
            return None, interpreter.error(node.token.traceback, f'random() amount must be above 0, not "{amount}"')



class d22FrozenSymbol(d22Symbol):
    def __init__(self, value, token):
        super().__init__(value, token, False)

    def __plus22__(self, n, i, o):
        return self._value.__plus22__(n, i, o)

    def __minus22__(self, n, i, o):
        return self._value.__minus22__(n, i, o)

    def __mul22__(self, n, i, o):
        return self._value.__mul22__(n, i, o)

    def __div22__(self, n, i, o):
        return self._value.__div22__(n, i, o)

    def __pow22__(self, n, i, o):
        return self._value.__pow22__(n, i, o)

    def __floor22__(self, n, i, o):
        return self._value.__floor22__(n, i, o)

    def __and22__(self, n, i, o):
        return self._value.__plus22__(n, i, o)

    def __or22__(self, n, i, o):
        return self._value.__minus22__(n, i, o)

    def __lessthan22__(self, n, i, o):
        return self._value.__mul22__(n, i, o)

    def __morethan22__(self, n, i, o):
        return self._value.__div22__(n, i, o)

    def __lessthaneq22__(self, n, i, o):
        return self._value.__pow22__(n, i, o)

    def __morethaneq22__(self, n, i, o):
        return self._value.__pow22__(n, i, o)

    def __eq22__(self, n, i, o):
        return self._value.__pow22__(n, i, o)

    def __neq22__(self, n, i, o):
        return self._value.__pow22__(n, i, o)

    def __repr__(self):
        return f'<Frozen: {self._value}>'

    def __d22repr__(self):
        return self.__repr__()


class d22IneffectualSymbol(d22Symbol):
    def __init__(self, value, token, booltype):
        super().__init__(value, token, booltype)

    def __plus22__(self, n, i, o):
        return o, None

    def __minus22__(self, n, i, o):
        return o, None

    def __mul22__(self, n, i, o):
        return o, None

    def __div22__(self, n, i, o):
        return o, None

    def __pow22__(self, n, i, o):
        return o, None

    def __floor22__(self, n, i, o):
        return o, None

    def __and22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __or22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __lessthan22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __morethan22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __lessthaneq22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __morethaneq22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __eq22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __neq22__(self, n, i, o):
        return d22Symbol(self._value, n.token, self._bool), None

    def __repr__(self):
        return f'<Ineffectual: {self._value}>'

    def __d22repr__(self):
        return self.__repr__()