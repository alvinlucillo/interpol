from enum import Enum
import math


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
            "WITH", "STORE", "IN", "INPUT",
            "PRINT", "PRINTLN", "ADD", "SUB",
            "MUL", "DIV", "MOD", "RAISE",
            "ROOT", "MEAN", "DIST", "AND"];

types = [11, 12, 16, 17,
         18, 19, 20, 21,
         22, 23, 26, 27,
         28, 29, 30, 31,
         32, 33, 34, 35]


class Token:
    def __init__(self, _type, _value, _line_no):
        self.type = _type
        self.value = _value
        self.line_no = _line_no

    @staticmethod
    def get_token_type(_type):
        for i, typ in enumerate(keywords):
            if typ == _type:
                return TokenType(types[i])
        return None

    def is_arithmetic_operator(self):
        return TokenType.BASIC_OPERATOR_ADD.value <= self.type.value <= TokenType.ADVANCED_OPERATOR_DIST.value

    def has_two_operators(self):
        return TokenType.BASIC_OPERATOR_ADD.value <= self.type.value <= TokenType.ADVANCED_OPERATOR_ROOT.value

    def get_type(self): return self.type

    def get_value(self): return self.value

    def get_line_no(self): return self.line_no


class Lexer:
    def __init__(self, _code):
        self.code = _code
        self.index = -1
        self.char = None
        self.line_no = 1
        self.line = ""

    def get_line(self):
        return self.line

    # Move to next character
    def next_char(self):
        if (self.index + 1) < len(self.code):
            self.index += 1
            self.char = self.code[self.index]

            self.line += self.char

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
                    token = Token(token_type, text, self.line_no)
                elif text.isalpha() and len(text) < 50 and text[0].islower():
                    token = Token(TokenType.IDENTIFIER, text, self.line_no)
                else:
                    raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.line_no, self.line)

            # If the first char is double quotes, it can be a string
            elif self.char == '[':
                text = self.advance_chars(']')

                if not (len(text) > 1 and text[0] == '[' and text[len(text) - 1] == ']'):
                    self.throw_error()

                text = text[1:len(text)-1]

                token = Token(TokenType.STRING, text, self.line_no)

            # If first char is numeric, it can be an integer
            elif self.char.isdigit():
                text = self.advance_chars()
                if text.isdigit():
                    token = Token(TokenType.NUMBER, text, self.line_no)
                else:
                    raise InterpreterError(InterpreterError.INVALID_DATA_TYPE, self.line_no, self.line)

            # Delimiter
            elif self.char == "\n":
                token = Token(TokenType.END_OF_STATEMENT, "EOS", self.line_no)
                self.line_no += 1
                self.line = self.line[0:len(self.line)-1]

            else:
                raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.line_no, self.line)

            # Returns token when it is already created
            if token is not None:
                return token

        self.line_no += 1
        token = Token(TokenType.END_OF_FILE, "EOF", self.line_no)

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
            self.line = self.line[0:len(self.line)-1]

        return self.code[start_pos: self.index + 1]

    # Returns true if char is in printable ASCII chart except for tab
    def is_printable_ascii_char(self):
        return 32 <= ord(self.char) <= 126 or 9 <= ord(self.char) <= 10

    def throw_error(self, token):
        raise InterpreterError


class Parser:
    def __init__(self, _lexer):
        self.lexer = _lexer
        self.token = None
        self.tokens = []
        self.variables = {}

    def get_current_line(self): return self.lexer.line
    def clear_current_line(self): self.lexer.line = ""

    def get_tokens(self): return self.tokens

    def variable_exists(self, name): return name in self.variables

    def declare_variable(self, _name, _type, _value=None):
        if self.variable_exists(_name):
            raise InterpreterError(InterpreterError.DUPLICATE_VARIABLE, self.token.line_no, self.get_current_line())

        variable = Variable(_name, _type, _value)
        self.variables[_name] = variable

    def assign_value_variable(self, name, value):
        if not (self.variable_exists(name)):
            raise InterpreterError(InterpreterError.VARIABLE_NOT_DECLARED, self.token.line_no, self.get_current_line())

        variable = self.get_variable(name)

        if not (variable.type == TokenType.NUMBER and str(value).isnumeric() or \
                (variable.type == TokenType.STRING and not str(value).isnumeric())):
            raise InterpreterError(InterpreterError.INCOMPATIBLE_DATE_TYPE, self.token.line_no, self.get_current_line())

        variable.value = value
        self.variables[name] = variable

    def get_variable(self, name): return self.variables.get(name)

    def next_token(self):
        self.token = self.lexer.next_token()

        if self.token is not None:
            self.tokens.append(self.token)

        return self.token

    # Main parser logic
    def execute(self):
        try:
            while self.next_token().type is not TokenType.END_OF_FILE:
                if self.token.type is TokenType.PROGRAM_BEGIN:
                    self.next_token()
                elif self.token.type is TokenType.OUTPUT or self.token.type is TokenType.OUTPUT_WITH_LINE:
                    if self.token.type is TokenType.OUTPUT:
                        self.print("")
                    else:
                        self.print("\n")

                elif self.token.type is TokenType.DECLARATION_INT or self.token.type is TokenType.DECLARATION_STRING:
                    self.assign()

                elif self.token.type is TokenType.ASSIGN_KEY:
                    self.store()

                elif self.token.type is TokenType.PROGRAM_END:
                    self.next_token()
                    break

                if self.token.type is not TokenType.END_OF_STATEMENT and \
                        self.next_token().type is not TokenType.END_OF_STATEMENT:
                    raise InterpreterError(InterpreterError.INVALID_EXPRESSION, self.token.line_no,
                                           self.get_current_line())

                self.clear_current_line()

        except InterpreterError as e:
            print(str(e))

    # Evaluates the expression to reach its value through recursion
    def evaluate_expression(self):

        if not (self.token.is_arithmetic_operator() or self.token.type is TokenType.IDENTIFIER or
                self.token.type is TokenType.NUMBER or self.token.type is TokenType.STRING):
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        value = None

        if self.token.type is TokenType.IDENTIFIER:
            variable = self.get_variable(self.token.value)
            value = variable.value

            if str(value).isnumeric():
                value = int(value)

        if self.token.type is TokenType.NUMBER:
            value = int(self.token.value)

        if self.token.type is TokenType.STRING:
            value = self.token.value

        if self.token.has_two_operators():
            return self.two_operators_arithmetic()

        return value

    def store(self):
        self.next_token()
        expression_result = self.evaluate_expression()

        operator = self.next_token()

        if operator.type is not TokenType.ASSIGN_VAR_KEY:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        variable = self.next_token()

        if variable.type is not TokenType.IDENTIFIER:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        self.assign_value_variable(variable.value, expression_result)

    def assign(self):
        declaration_type = self.token
        identifier = self.next_token()
        value = None

        if identifier.type is not TokenType.IDENTIFIER:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        operator = self.next_token()

        if operator.type is TokenType.DECLARATION_ASSIGN_WITH_KEY:
            self.next_token()
            value = self.evaluate_expression()

            if not (value is not None and
                    ((declaration_type.type is TokenType.DECLARATION_INT and str(value).isnumeric()) or
                        declaration_type.type is TokenType.DECLARATION_STRING and not str(value).isnumeric())):

                raise InterpreterError(InterpreterError.INCOMPATIBLE_DATE_TYPE, self.token.line_no,
                                       self.get_current_line())
        elif operator.type is TokenType.END_OF_STATEMENT:
            pass
        else:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        if declaration_type.type is TokenType.DECLARATION_INT:
            variable_type = TokenType.NUMBER
        else:
            variable_type = TokenType.STRING

        self.declare_variable(identifier.value, variable_type, value)

    def two_operators_arithmetic(self):
        operator = self.token.type

        self.next_token()
        operand1 = self.evaluate_expression()

        self.next_token()
        operand2 = self.evaluate_expression()

        if operator == TokenType.BASIC_OPERATOR_ADD:
            return operand1 + operand2
        if operator == TokenType.BASIC_OPERATOR_SUB:
            return operand1 - operand2
        if operator == TokenType.BASIC_OPERATOR_MUL:
            return operand1 * operand2
        if operator == TokenType.BASIC_OPERATOR_DIV:
            return operand1 / operand2
        if operator == TokenType.BASIC_OPERATOR_MOD:
            return operand1 % operand2
        if operator == TokenType.ADVANCED_OPERATOR_EXP:
            return operand1 ** operand2
        if operator == TokenType.ADVANCED_OPERATOR_ROOT:
            return operand2 ** (1/float(operand1))

    def print(self, _end):
        expression = self.next_token()

        value = self.evaluate_expression()

        print(value, end=_end)

    def get_literal_identifier(self):
        value = None

        if self.token.type == TokenType.STRING or self.token.type == TokenType.NUMBER:
            value = self.token.value
            if value.isnumeric():
                return int(value)

        elif self.token.type == TokenType.IDENTIFIER:
            return self.get_variable(self.token.value)

        return value


class Variable:
    def __init__(self, _name, _type, _value):
        self.name = _name
        self.type = _type
        self.value = _value


class InterpreterError(Exception):

    INVALID_SYNTAX = "Invalid syntax"
    VARIABLE_NOT_DECLARED = "Variable is not declared"
    INVALID_ARITHMETIC_OPERATION = "Invalid arithmetic operation"
    INVALID_EXPRESSION = "Invalid expression"
    INVALID_DATA_TYPE = "Invalid data type"
    DUPLICATE_VARIABLE = "Duplicate variable declaration"
    INCOMPATIBLE_DATE_TYPE = "Incompatible data type"
    INVALID_DATA_TYPE_INPUT = "Invalid data type input"
    INVALID_EOF = "Invalid end of file"
    FILE_EMPTY = "File is empty"
    FILE_NOT_FOUND = "File not found"
    INVALID_FILE = "Invalid file"

    def __init__(self, _message, line_no, line):
        self.message = _message + " at line number [ " + str(line_no) + " ]" + "\n" + \
            " ----> " + line
        super().__init__(self.message)


def main():
    welcome_message = "========  INTERPOL INTERPRETER STARTED   ========\n"
    output_message = "================ INTERPOL OUTPUT ================\n"
    output_message_start = "----------------  OUTPUT START  ---------------->"
    output_message_end = "<----------------- OUTPUT END -------------------"
    token_list_header = "\n\n========= INTERPOL LEXEMES/TOKENS TABLE =========\n"
    token_list_columns = "LINE NO.  TOKENS                          LEXEMES"

    print(welcome_message)

    # file_path = input("Enter INTERPOL file (.ipol): ")
    file_path = "C:\\Users\\Alvin Lucillo\\PycharmProjects\\interpol\\venv\\test1.ipol"
    file = open(file_path, 'r')
    contents = file.read()

    print(output_message)
    print(output_message_start)

    lexer = Lexer(contents)
    parser = Parser(lexer)

    parser.execute()

    #print(token_list_header)
    #print(token_list_columns)

    for token in parser.get_tokens():
        pass #print(str(token.line).ljust(10) + TokenType(token.type).name.ljust(32) + token.value)


# Execute INTERPOL program automatically if running the module itself
if __name__ == '__main__':
    main()
