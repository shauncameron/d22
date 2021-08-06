class d22Traceback:
    def __init__(self, text, col):
        self.text = text
        self.col = col

    def find(self) -> (int, int, str):
        text = self.text
        col = self.col

        if len(text) < col:
            raise Exception('Internal traceback exception: len(text) < col. Apologies for the inconvenience')

        index = 0
        line = 0
        linecol = 0
        linetext = ''
        while index != col:
            if text[index] == '\n':
                line += 1
                linetext = ''
                linecol = 0
            else:
                linetext += text[index]
                index += 1
                linecol += 1

        while (index < len(text)) and (text[index] != '\n'):
            linetext += text[index]
            index += 1

        return linecol, line, linetext

    def printable(self, printabletype, message=''):
        linecol, line, text = self.find()  # Linecol, line, text
        return f'd22 {printabletype} (ln:{line + 1}, col:{linecol})' + '\n' + f'    Message: {message}' + '\n' + f'    Line:' + '\n' + f'        ' + (' ' * linecol) + '▼' + '\n' + f'        ' + text + '\n' + f'        ' + (' ' * linecol) + '▲'



class d22Error:
    def __init__(self, traceback: d22Traceback, message: str):
        self.traceback = traceback
        self.message = message

    def printable(self):
        return self.traceback.printable('Error', self.message)