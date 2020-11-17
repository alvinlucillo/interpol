from enum import Enum


class TokenType(Enum):
    # Data type
    NUMBER = 0
    STRING = 1
    # Identifier
    IDENTIFIER = 6
    # Scope
    PROGRAM_BEGIN = 11
    PROGRAM_END = 12
    END_OF_STATEMENT = 13
    END_OF_FILE = 14
    # Declaration
    DECLARATION_STRING = 16
    DECLARATION_INT = 17
    DECLARATION_ASSIGN_WITH_KEY = 18
    ASSIGN_KEY = 19
    ASSIGN_VAR_KEY = 20
    # Input output
    INPUT = 21
    OUTPUT = 22
    OUTPUT_WITH_LINE = 23
    # Basic math operation
    BASIC_OPERATOR_ADD = 26
    BASIC_OPERATOR_SUB = 27
    BASIC_OPERATOR_MUL = 28
    BASIC_OPERATOR_DIV = 29
    BASIC_OPERATOR_MOD = 30
    # Advanced math operation
    ADVANCED_OPERATOR_EXP = 31
    ADVANCED_OPERATOR_ROOT = 32
    ADVANCED_OPERATOR_AVE = 33
    ADVANCED_OPERATOR_DIST = 34
    DISTANCE_SEPARATOR = 35


keywords = ["BEGIN", "END", "VARSTR", "VARINT",
            "WITH", "STORE", "IN",  "INPUT",
            "PRINT", "PRINTLN", "ADD", "SUB",
            "MUL", "DIV", "MOD", "RAISE",
            "ROOT", "MEAN", "DIST", "AND"];

types = [11, 12, 16, 17,
         18, 19, 20, 21,
         22, 23, 26, 27,
         28, 29, 30, 31,
         32, 33, 34, 35]


class Token:
    def __init__(self, _type, _value, _line):
        self.type = _type
        self.value = _value
        self.line = _line

    @staticmethod
    def get_token_type(_type):
        for i, typ in enumerate(keywords):
            if typ == _type:
                return TokenType(types[i])
        return None

    def is_arithmetic_operator(self):
        return TokenType.BASIC_OPERATOR_ADD <= self.type <= TokenType.ADVANCED_OPERATOR_DIST

    def get_type(self): return self.type

    def get_value(self): return self.value


class Lexer:
    def __init__(self, _code):
        self.code = _code
        self.index = -1
        self.char = None
        self.line = 1

    # Move to next character
    def next_char(self):
        if (self.index + 1) < len(self.code):
            self.index += 1
            self.char = self.code[self.index]

            # Check if the character is an acceptable ASCII code
            if not self.is_printable_ascii_char():
                self.throw_error()
        else:
            self.char = None

        return self.char

    # Move to next token
    def next_token(self):
        token = None

        while self.next_char() is not None:
            # Skip whitespace
            if self.char in ['\r', ' ', '\t']:
                pass

            # If first char is alphabetic, it can be a keyword
            elif self.char.isalpha():
                text = self.advance_chars()
                token_type = Token.get_token_type(text)

                if token_type is not None:
                    token = Token(token_type, text, self.line)
                elif text.isalpha() and len(text) < 50 and text[0].islower():
                    token = Token(TokenType.IDENTIFIER, text, self.line)
                else:
                    self.throw_error()

            # If the first char is double quotes, it can be a string
            elif self.char == '[':
                text = self.advance_chars(']')

                if not (len(text) > 1 and text[0] == '[' and text[len(text) - 1] == ']'):
                    self.throw_error()

                text = text[1:len(text)-1]

                token = Token(TokenType.STRING, text, self.line)

            # If first char is numeric, it can be an integer
            elif self.char.isdigit():
                text = self.advance_chars()
                if text.isdigit():
                    token = Token(TokenType.NUMBER, text, self.line)
                else:
                    self.throw_error()

            # Delimiter
            elif self.char == "\n":
                token = Token(TokenType.END_OF_STATEMENT, "EOS", self.line)
                self.line += 1

            else:
                self.throw_error()

            # Returns token when it is already created
            if token is not None:
                return token

        self.line += 1
        token = Token(TokenType.END_OF_FILE, "EOF", self.line)

        return token

    # Returns characters before any whitespace
    def advance_chars(self, delimiter=None):
        start_pos = self.index
        # Continue until EOL, delimiter is reached or space is reached
        while self.next_char() is not None and \
                ((not self.char.isspace() and delimiter is None) or
                 (delimiter is not None))\
                and not self.char == delimiter:
            pass
        # If loop above terminates due to space, move back cursor to last non-space char
        if self.char is not None and self.char.isspace():
            self.index -= 1

        return self.code[start_pos: self.index + 1]

    # Returns true if char is in printable ASCII chart except for tab
    def is_printable_ascii_char(self):
        return 32 <= ord(self.char) <= 126 or 9 <= ord(self.char) <= 10

    def throw_error(self, token):
        raise LexerError


class Parser:
    def __init__(self, _lexer):
        self.lexer = _lexer
        self.token = None
        self.tokens = []

    def get_tokens(self):
        return self.tokens

    def next_token(self):
        self.token = self.lexer.next_token()

        if self.token is not None:
            self.tokens.append(self.token)

        return self.token

    def execute(self):
        while self.next_token() is not TokenType.END_OF_FILE:
            if self.token.type is TokenType.OUTPUT:
                self.print()

    def evaluate_expression(self):
        if self.token.type == TokenType.BASIC_OPERATOR_ADD:
            self.add()
        return ""

    def add(self):
        self.next_token()

        operand1 = self.get_literal_identifier_value()
        if operand1 is None:
            if self.token.is_arithmetic_operator():
                operand1 = self.evaluate_expression()

        self.next_token()

        operand2 = self.get_literal_identifier_value()
        if operand2 is None:
            if self.token.is_arithmetic_operator():
                operand2 = self.evaluate_expression()

        return operand1 + operand2

    def print(self):
        self.next_token()

        value = self.get_literal_identifier_value()
        if value is None:
            if self.token.is_arithmetic_operator():
                value = self.evaluate_expression()

        print(value)

    def get_literal_identifier_value(self):
        value = None
        if self.token.type == TokenType.STRING or self.token.type == TokenType.NUMBER:
            value = self.token.value
        elif self.token.type == TokenType.IDENTIFIER:
            pass

        return value


class LexerError(Exception):
    def __init__(self, _message="The syntax is incorrect."):
        self.message = _message
        super().__init__(self.message)


class ParserError(Exception):
    def __init__(self, _message="The syntax is incorrect."):
        self.message = _message
        super().__init__(self.message)


def main():
    welcome_message = "========  INTERPOL INTERPRETER STARTED   ========\n"
    output_message = "================ INTERPOL OUTPUT ================\n"
    token_list_header = "========= INTERPOL LEXEMES/TOKENS TABLE =========\n"
    token_list_columns = "LINE NO.  TOKENS                          LEXEMES"

    print(welcome_message)

    # file_path = input("Enter INTERPOL file (.ipol): ")
    file_path = "C:\\Users\\Alvin Lucillo\\PycharmProjects\\interpol\\venv\\test1.ipol"
    file = open(file_path, 'r')
    contents = file.read()

    print(output_message)

    lexer = Lexer(contents)
    parser = Parser(lexer)

    parser.execute()

    print(token_list_header)
    print(token_list_columns)

    for token in parser.get_tokens():
        print(str(token.line).ljust(10) + TokenType(token.type).name.ljust(32) + token.value)


# Execute INTERPOL program automatically if running the module itself
if __name__ == '__main__':
    main()
