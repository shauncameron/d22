from d22.d22lexer import *
from d22.d22parser import *
from d22.d22symbol import *
from d22.d22interpreter import *

default_symbols = SymbolTable()


class RollResult:
    def __init__(self, rlexing, rparser, rparsing, rinterpreter, rinterpretation, rresult):
        self.lexing = rlexing
        self.parser = rparser
        self.parsing = rparsing
        self.interpreter = rinterpreter
        self.interpretation = rinterpretation
        self.result = rresult
    def plainprintable(self):
        return f"""{self.parsing.__22_plain__()} = {self.interpretation.__d22display__()}"""
    def evalprintable(self):
        return f"""{self.parsing.__displayeval__()} = {self.interpretation}"""

def roll(string: str = '?(h(2d8,2d6),2d4,2d3)<4:^??.', symboltable: SymbolTable = default_symbols):
    SOF, EOF = d22Traceback(string, 0), d22Traceback(string, len(string)-1)

    if not len(string):
        return None, d22Error(SOF, 'Will not lex an empty string')

    lexing, error = lex(string)
    if error: return None, error

    if not len(lexing):
        return None, d22Error(SOF, 'Will not parse an empty token set')

    parser = d22Parser(lexing, string)
    parsing, error = parser.parse()
    if error: return None, error

    interpreter = d22Interpreter(parsing, string, symboltable)
    interpretation, error = interpreter.visit(parsing)
    if error: return None, error

    result, error = interpretation.value(parsing, interpreter)
    if error: return None, error

    return RollResult(lexing, parser, parsing, interpreter, interpretation, result), None


if __name__ == '__main__':
    query = """$(10 ** 3 / 4)"""

    while (query := input('>>> ')) != 'OUT':
        result, error = roll(query)
        if error: print(error.printable())
        else:
            if error: print(error.printable())
            else:
                print(result.parsing.__22_plain__(), '=', result.interpretation.__d22display__())
                print(result.parsing.__displayeval__(), '=', result.interpretation)


