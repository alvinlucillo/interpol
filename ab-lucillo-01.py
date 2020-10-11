from enum import Enum


class TokenType(Enum):
    # Data types
    INT = 0
    STRING = 1
    # User identifiers
    IDENTIFIER = 10
    # Math operators
    ADD = 20
    SUB = 21
    MUL = 22
    DIV = 23
    MOD = 24
    # Other identifiers
    BEGIN = 30
    END = 31
    PRINT = 32
    PRINTLN = 33
    # Delimiter
    NEWLINE = 40
    # Comment
    COMMENT = 50


class Token:
    def __init__(self, _type, _value):
        self.type = _type
        self.value = _value

    def __str__(self):
        return str(str(self.type) + ":" + self.value)

    @staticmethod
    def get_keyword(text):
        for tokenType in TokenType:
            if tokenType.name == text and 20 <= tokenType.value <= 39:
                return tokenType
        return None

    def is_type(self, _type):
        return self.type == _type

    def is_math_operator(self):
        keyword = self.get_keyword(self.value)
        return keyword is not None and 20 <= keyword.value <= 29


class LexicalAnalyzer:
    def __init__(self, _code):
        self.code = _code
        self.index = -1
        self.char = None

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
                token_type = Token.get_keyword(text)

                if text.isalpha() and text.isupper():
                    token = Token(token_type, text)
                else:
                    self.throw_error()

            # If the first char is double quotes, it can be a string
            elif self.char == '\"':
                text = self.advance_chars("\"")

                if not (len(text) > 1 and text[0] == '\"' and text[len(text) - 1] == '\"'):
                    self.throw_error()

                token = Token(TokenType.STRING, text)

            # If first char is numeric, it can be an integer
            elif self.char.isdigit():
                text = self.advance_chars()
                if text.isdigit():
                    token = Token(TokenType.INT, text)
                else:
                    self.throw_error()

            # If first char is #, it is a comment
            elif self.char == "#":
                token = Token(TokenType.COMMENT, self.code)

            # Delimiter
            elif self.char == "\n":
                token = Token(TokenType.NEWLINE, self.char)

            else:
                self.throw_error()

            # Returns token when it is already created
            if token is not None:
                return token

    # Returns characters before any whitespace
    def advance_chars(self, delimiter=None):
        start_pos = self.index
        while self.next_char() is not None and \
                ((not self.char.isspace() and delimiter is None) or
                 (self.char.isspace() and delimiter == "\"" or not self.char.isspace() and delimiter == "\""))\
                and not self.char == delimiter:
            pass

        if self.char is not None and self.char.isspace():
            self.index -= 1

        return self.code[start_pos: self.index + 1]

    # Returns true if char is in printable ASCII chart except for tab
    def is_printable_ascii_char(self):
        return 32 <= ord(self.char) <= 126 or 9 <= ord(self.char) <= 10

    def throw_error(self):
        raise LexerError


class LexerError(Exception):
    def __init__(self, _message="The syntax is incorrect."):
        self.message = _message
        super().__init__(self.message)


class ParserError(Exception):
    def __init__(self, _message="The syntax is incorrect."):
        self.message = _message
        super().__init__(self.message)


class TokenAnalyzer:

    def __init__(self, _lexer):
        self.lexer = _lexer
        self.token = None
        self.analyzer_started = False
        self.remaining_tokens = []
        self.terminate = False

    def set_lexer(self, _lexer):
        self.lexer = _lexer
        self.token = None
        self.remaining_tokens = []

    def next_token(self):
        self.token = self.lexer.next_token()
        return self.token

    def evaluate(self):

        try:
            self.next_token()

            if self.token is not None:
                if self.token.is_type(TokenType.COMMENT):
                    self.comment()
                elif self.token.is_type(TokenType.BEGIN):
                    self.begin()
                elif self.token.is_type(TokenType.END):
                    self.end()
                    return False
                elif not self.analyzer_started:
                    raise ParserError
                elif self.token.is_type(TokenType.PRINT) or self.token.is_type(TokenType.PRINTLN):
                    self.print()
                elif self.token.is_math_operator():
                    self.math_operation()
                else:
                    raise ParserError

        except LexerError as e:
            print(str(e))
        except ParserError as e:
            print(str(e))

        return True

    def begin(self):
        self.get_remaining_tokens()

        if len(self.remaining_tokens) > 0:
            raise ParserError

        if not self.analyzer_started:
            print("The syntax is correct. Beginning syntax checker.")
            self.analyzer_started = True
        else:
            self.print_correct_syntax()

        return True

    def print(self):
        self.get_remaining_tokens()

        if not (len(self.remaining_tokens) == 1 and self.remaining_tokens[0].is_type(TokenType.STRING)):
            raise ParserError
        else:
            self.print_correct_syntax()

    def math_operation(self):
        self.get_remaining_tokens()

        if len(self.remaining_tokens) == 2 and \
                self.remaining_tokens[0].is_type(TokenType.INT) and self.remaining_tokens[1].is_type(TokenType.INT):
            self.print_correct_syntax()
        else:
            raise ParserError

    def comment(self):
        self.print_correct_syntax()

    def end(self):
        self.get_remaining_tokens()

        if len(self.remaining_tokens) > 0:
            raise ParserError

        print("Thank you for using the syntax checker.")

    def get_remaining_tokens(self):
        while self.next_token() is not None:
            self.remaining_tokens.append(self.token)

    @staticmethod
    def print_correct_syntax():
        print("The syntax is correct.")


def main():
    welcome_message = "INTERPOL Syntax Checker\nInput BEGIN to begin. Input END to end."
    print(welcome_message)

    parser = TokenAnalyzer(LexicalAnalyzer(input()))

    # Continue to ask for input until END is entered
    while parser.evaluate():
        parser.set_lexer(LexicalAnalyzer(input()))


# Execute INTERPOL program automatically if running the module itself
if __name__ == '__main__':
    main()
