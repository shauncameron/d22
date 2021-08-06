class AST:

    def __22_plain__(self) -> str:
        pass

class BinaryOperation(AST):
    def __repr__(self):
        return f'({self.left}  {self.operator.value}  {self.right})'

    def getleft(self):
        return self.left.left()

    def getright(self):
        return self.right.right()

    def __22_plain__(self):
        return f'{self.left.__22_plain__()}  {self.operator.value}  {self.right.__22_plain__()}'

    def __pydict__(self):
        return {'type': 'binaryop', 'binaryop': {'left': self.left.__pydict__(), 'op': self.operator.value, 'right': self.right.__pydict__()}}

    def __init__(self, left, operator, right, token):
        self.left = left
        self.operator = operator
        self.right = right
        self.token = token
        self.lefteval = None
        self.righteval = None

    def __displayeval__(self):
        return f'{self.lefteval if self.lefteval else ""} {self.operator.value} {self.righteval if self.righteval else ""}'

    @property
    def evaluation(self):
        return self.__displayeval__()

    @evaluation.setter
    def evaluation(self, n):
        pass

    def __str__(self):
        return self.__repr__()


class BinaryBooleanOperation(BinaryOperation):
    def __init__(self, left, operator, right, token):
        super().__init__(left, operator, right, token)


class UnaryOperation(AST):
    def __repr__(self):
        return f'{self.value}'

    def __22_plain__(self):
        return f'{self.value}'

    def left(self):
        return self

    def right(self):
        return self

    def __pydict__(self):
        return {'type': 'unaryop', 'unaryop': {'type': 'undef', 'value': self.value}}

    def __init__(self, value, token):
        self.value = value
        self.token = token
        self.evaluation = None

    def __displayeval__(self):
        return f'{self.evaluation if self.evaluation else ""}'

    def __str__(self):
        return self.__repr__()

class UOPFrozen(UnaryOperation):
    def __init__(self, value, token):
        super().__init__(value, token)


class UOPAssign(UnaryOperation):
    def __repr__(self):
        return f'({self.identifier} <- {self.value})'

    def __init__(self, identifier, value, token):
        self.identifier = identifier
        super().__init__(value, token)


class UOPReference(UnaryOperation):
    def __init__(self, identifier, token):
        super().__init__(identifier, token)


class UOPExpressionChain(UnaryOperation):
    def __repr__(self):
        message = f'(? {self.ifcon} : {self.ifthen}'
        for elifcon, elifthen in self.elifs:
            message += f' ? {elifcon} : {elifthen}'
        message += f' ?? {self.elsethen})'
        return message

    def __init__(self, ifcon, ifthen, elifs, elsethen, token):
        super().__init__(ifcon, token)
        self.ifcon = ifcon
        self.ifthen = ifthen
        self.elifs = elifs
        self.elsethen = elsethen

class UOPExpressionSequence(UnaryOperation):
    def __repr__(self):
        message = f'{", ".join([f"{x}" for x in self.value])}'
        return message

    def __22_plain__(self):
        return self.__repr__()

    def __init__(self, expressions, token):
        super().__init__(expressions, token)


class UOPNot(UnaryOperation):
    def __init__(self, expression, token):
        super().__init__(expression, token)


class UOPDrop(UnaryOperation):
    def __init__(self, expression, token):
        super().__init__(expression, token)


class UOPNegative(UnaryOperation):
    def __init__(self, expression, token):
        super().__init__(expression, token)


class UOPHighest(UnaryOperation):
    def __repr__(self):
        return f'h{self.amount + " " if self.amount else " "}of {self.value}'

    def __init__(self, amount, expression, token):
        self.amount = amount
        super().__init__(expression, token)

class UOPLowest(UnaryOperation):
    def __repr__(self):
        return f'l{self.amount + " " if self.amount else " "}of {self.value}'

    def __init__(self, amount, expression, token):
        self.amount = amount
        super().__init__(expression, token)


class UOPRandom(UnaryOperation):
    def __repr__(self):
        return f'r{self.amount + " " if self.amount else " "}from {self.value}'

    def __init__(self, amount, expression, token):
        self.amount = amount
        super().__init__(expression, token)

class UOPDiceRoll(UnaryOperation):
    def __repr__(self):
        return f'{self.amount}d(1-{self.value})'

    def __22_plain__(self):
        return f'{"" if not self.amount else self.amount}d{self.value}'

    def __init__(self, amount, value, token):
        self.amount = amount
        super().__init__(value, token)


class UOPNumber(UnaryOperation):
    def __init__(self, value, token):
        super().__init__(value, token)


class UOPiPositive(UnaryOperation):
    def __init__(self, token):
        super().__init__(token, token)


class UOPiNegative(UnaryOperation):
    def __init__(self, token):
        super().__init__(token, token)


class UOPCaret(UnaryOperation):
    def __repr__(self):
        return f'(Contextual Lambda)'

    def __22_plain__(self):
        return f'.'

    def __init__(self, token):
        super().__init__(token, token)


class UOPLambda(UnaryOperation):
    def __repr__(self):
        return f'$({self.value})'

    def __22_plain__(self):
        return f'$({self.value})'

    def __init__(self, value, token):
        super().__init__(value, token)


class UOPDot(UnaryOperation):
    def __repr__(self):
        return f'(Contextual Result)'

    def __22_plain__(self):
        return f'.'

    def __init__(self, token):
        super().__init__(token, token)

class Annotated(UnaryOperation):
    def __repr__(self):
        return f'{self.value} {self.annotation}'

    def __22_plain__(self):
        return f'{self.value} {self.annotation}'

    def __init__(self, value, annotation, token):
        self.annotation = annotation
        super().__init__(value, token)