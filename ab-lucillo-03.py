# Student: Alvin Lucillo
# Description: INTERPOL for IS214 Assignment #3


from enum import Enum
import pathlib
import os


# These are the mapping of Token Types and their corresponding Lexem names for Lexem table
# For example, the value of keywords[0] is 11, which corresponds to TokenType.PROGRAM_BEGIN
keywords = ["BEGIN", "END", "VARSTR", "VARINT",
            "WITH", "STORE", "IN", "INPUT",
            "PRINT", "PRINTLN", "ADD", "SUB",
            "MUL", "DIV", "MOD", "RAISE",
            "ROOT", "MEAN", "DIST", "AND"]

types = [11, 12, 16, 17,
         18, 19, 20, 21,
         22, 23, 26, 27,
         28, 29, 30, 31,
         32, 33, 34, 35]


# Token Type enumeration for use in operations
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


# Token class that holds token information
class Token:
    def __init__(self, _type, _value, _line_no):
        self.type = _type
        self.value = _value
        self.line_no = _line_no

    # Returns the TokenType instance if it matches any of the defined keywords
    @staticmethod
    def get_token_type(_type):
        for i, typ in enumerate(keywords):
            if typ == _type:
                return TokenType(types[i])
        return None

    # Checks if the Token is an arithmetic operator
    def is_arithmetic_operator(self):
        return TokenType.BASIC_OPERATOR_ADD.value <= self.type.value <= TokenType.ADVANCED_OPERATOR_DIST.value

    # Checks if the Token requires only two parameters
    def has_two_operators(self):
        return TokenType.BASIC_OPERATOR_ADD.value <= self.type.value <= TokenType.ADVANCED_OPERATOR_ROOT.value

    # Returns the current line number
    def get_line_no(self): return self.line_no


# Variable class to hold programmer-defined identifier information
class Variable:
    def __init__(self, _name, _type, _value):
        self.name = _name
        self.type = _type
        self.value = _value


# Value class to hold the values returned by expressions
class Value:
    def __init__(self, _type, _value):
        self.type = _type
        self.value = _value


# InterpreterError exception class for INTERPOL-specific errors
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


# Lexer class to tokenize the program source code
class Lexer:
    def __init__(self, _code):
        self.code = _code
        self.index = -1
        self.char = None
        self.line_no = 1
        self.line = ""

    # Move to the next character
    def next_char(self):
        if (self.index + 1) < len(self.code):
            self.index += 1
            self.char = self.code[self.index]

            self.line += self.char

            # Check if the character is an acceptable ASCII code
            if not self.is_printable_ascii_char(self.char):
                raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.line_no, self.line)
        else:
            self.char = None

        return self.char

    # Get the next token
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

                # Token is a keyword of the program
                if token_type is not None:
                    token = Token(token_type, text, self.line_no)
                # Token is an invalid identifier
                elif text[0].isalpha() and len(text) < 50 and self.is_printable_ascii_string(text):
                    token = Token(TokenType.IDENTIFIER, text, self.line_no)
                # Token is not a keyword nor an identifier
                else:
                    raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.line_no, self.line)

            # If the first char is double quotes, it can be a string
            elif self.char == '"':
                text = self.advance_chars('"')

                # If the token is not properly enclosed by an ending double quotes
                if not (len(text) > 1 and text[0] == '"' and text[len(text) - 1] == '"'):
                    raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.line_no, self.line)
                # Retrieve the string literal excluding the double quotes
                text = text[1:len(text)-1]

                token = Token(TokenType.STRING, text, self.line_no)

            # If first char is numeric or has negative or decimal point sign, it can be a number
            elif self.char.isdigit() or self.char == "-" or self.char == ".":

                text = self.advance_chars()
                typ = self.get_type(text)
                # It is a floating-point value
                if typ == 1:
                    raise InterpreterError(InterpreterError.INVALID_DATA_TYPE, self.line_no, self.line)
                # It is a string value
                elif typ == 2:
                    raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.line_no, self.line)

                token = Token(TokenType.NUMBER, text, self.line_no)

            # If starts with #, it is a comment
            elif self.char == "#":
                # Advance chars until newline or end of statement is reached
                self.advance_chars('\n')

            # End of statement reached
            elif self.char == "\n":
                token = Token(TokenType.END_OF_STATEMENT, "EOS", self.line_no)
                self.line_no += 1
                # Remove the newline character
                self.line = self.line[0:len(self.line)-1]
            # If an unrecognized token is detected
            else:
                raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.line_no, self.line)

            # Returns token when it is already created; terminates the while statement
            if token is not None:
                return token
        # Increments the current line number; if this is reached, it means there are no tokens detected
        self.line_no += 1
        token = Token(TokenType.END_OF_FILE, "EOF", self.line_no)

        return token

    @staticmethod
    # Returns the the type of the literal value
    # 0 is integer; 1 is float; 2 is non-numeric
    def get_type(text):
        typ = 0
        try:
            int(text)
        except ValueError:
            typ = 1
            try:
                float(text)
            except ValueError:
                typ = 2

        return typ

    # Returns characters before any whitespace
    def advance_chars(self, delimiter=None):
        start_pos = self.index

        # Continue to iterate characters until there are no more characters to read,
        #   character is a whitespace except when there's a delimiter (e.g. searching for strings enclosed in ""),
        #   character is not a delimiter and character is not end of line (\n)
        while self.next_char() is not None and \
                ((not self.char.isspace() and delimiter is None) or
                 (delimiter is not None))\
                and not self.char == delimiter and not self.char == '\n':
            pass

        # If loop above terminates due to space, move back cursor to last non-space char
        if self.char is not None and self.char.isspace():
            self.index -= 1
            self.line = self.line[0:len(self.line)-1]

        return self.code[start_pos: self.index + 1]

    # Returns true if char is in printable ASCII chart including tab and new line
    @staticmethod
    def is_printable_ascii_char(c, include_tab_nl=True):
        if include_tab_nl:
            return 32 <= ord(c) <= 126 or 9 <= ord(c) <= 10
        else:
            return 32 <= ord(c) <= 126

    def is_printable_ascii_string(self, string):
        for c in string:
            if not self.is_printable_ascii_char(c, False):
                return False
        return True


# Parser class that uses the tokens from the parser, checks the syntax and semantics of the tokens,
#  and executes the program
class Parser:
    def __init__(self, _lexer):
        self.lexer = _lexer
        self.token = None
        self.tokens = []
        self.variables = {}
        self.has_begin = False              # Flags that there is already a BEGIN statement
        self.has_end = False                # Flags that there is already an END statement
        self.prev_print_has_newline = True  # Flags that previous PRINT statement has a newline affixed to it
        self.prev_non_eos_line = None       # Contains the previous executable statement; used for Invalid end of file
        self.prev_non_eos_lineno = None     # Contains the previous line number of an executable statement
        self.longest_variable_length = 0    # Contains the longest variable name length for symbols table
        self.store_op_in_use = False        # Flags that STORE operation is in use

    # Main parser logic that checks each token and calls its corresponding method for further evaluation
    def execute(self):
        self.next_token()

        try:
            while True:
                # Make sure the first executable statement is BEGIN
                if not self.has_begin and self.token.type is not TokenType.END_OF_STATEMENT \
                        and self.token.type is not TokenType.PROGRAM_BEGIN or \
                        (self.has_end and self.token.type is TokenType.PROGRAM_END):
                    raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

                if self.token.type is TokenType.PROGRAM_BEGIN:
                    self.has_begin = True

                elif self.token.type is TokenType.OUTPUT or self.token.type is TokenType.OUTPUT_WITH_LINE:
                    if self.token.type is TokenType.OUTPUT:
                        self.print("")
                        self.prev_print_has_newline = False
                    else:
                        self.print("\n")
                        self.prev_print_has_newline = True

                elif self.token.type is TokenType.DECLARATION_INT or self.token.type is TokenType.DECLARATION_STRING:
                    self.assign()

                elif self.token.type is TokenType.ASSIGN_KEY:
                    self.store()

                elif self.token.type is TokenType.INPUT:
                    self.input()

                elif self.token.type is TokenType.PROGRAM_END:
                    self.has_end = True

                elif self.token.is_arithmetic_operator():
                    self.evaluate_expression()

                # Clears the current line if end of statement is reached (i.e. it is time for the next statement)
                if self.token.type is TokenType.END_OF_STATEMENT:
                    self.clear_current_line()

                prev_token = self.token
                self.next_token()

                # Skip to evaluation of token above if this is a completely new statement
                if prev_token.type is TokenType.END_OF_STATEMENT and self.token.type is not TokenType.END_OF_FILE:
                    continue
                # If end of file is reached, check if END was encountered, then terminate the loop
                if self.token.type is TokenType.END_OF_FILE:
                    if not self.has_end:
                        raise InterpreterError(InterpreterError.INVALID_EOF, self.prev_non_eos_lineno,
                                               self.prev_non_eos_line)
                    break
                # Expects that each method above should end with EOS
                if self.token.type is not TokenType.END_OF_STATEMENT:
                    raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        except InterpreterError as e:
            # Display the error message and prefix a newline if previous print has no newline
            print(('\n' if not self.prev_print_has_newline else '') + str(e), end="")

    # Evaluates the expression to reach its value through recursion algorithm
    # This is where literal values, variables, and arithmetic operators are evaluated
    def evaluate_expression(self):
        # Expression error if it is an incomplete expression (i.e. EOS is reached)
        if self.token.type is TokenType.END_OF_STATEMENT:
            raise InterpreterError(InterpreterError.INVALID_EXPRESSION, self.token.line_no, self.get_current_line())
        # Syntax error if it not a valid token in an expression
        elif not (self.token.is_arithmetic_operator() or self.token.type is TokenType.IDENTIFIER or
                  self.token.type is TokenType.NUMBER or self.token.type is TokenType.STRING):
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        value = None

        if self.token.type is TokenType.IDENTIFIER:
            variable = self.get_variable(self.token.value)

            if variable is None:
                raise InterpreterError(InterpreterError.VARIABLE_NOT_DECLARED, self.token.line_no,
                                       self.get_current_line())

            value = Value(variable.type, variable.value)

        if self.token.type is TokenType.NUMBER:
            value = Value(TokenType.NUMBER, self.token.value)

        if self.token.type is TokenType.STRING:
            value = Value(TokenType.STRING, self.token. value)

        if self.token.has_two_operators():
            return self.two_operators_arithmetic()

        # Checks the syntax for: MEAN <expr1> <expr2> <expr3> … <exprn>
        elif self.token.type is TokenType.ADVANCED_OPERATOR_AVE:
            count = 0
            sum_of_value = 0

            self.next_token()

            while self.token.type is not TokenType.END_OF_STATEMENT:
                if self.token.type is TokenType.ASSIGN_VAR_KEY and self.store_op_in_use:
                    break

                value = self.evaluate_expression()
                self.check_compatibility(TokenType.NUMBER, value)

                sum_of_value += int(str(value.value))
                count += 1
                self.next_token()

            try:
                result = Value(TokenType.NUMBER, int(sum_of_value/count))
            except ArithmeticError:
                raise InterpreterError(InterpreterError.INVALID_ARITHMETIC_OPERATION, self.token.line_no,
                                       self.get_current_line())

            return result
        # Checks the syntax for: DIST <expr1> <expr2> AND <expr3> <expr4>
        elif self.token.type is TokenType.ADVANCED_OPERATOR_DIST:
            self.next_token()
            expr1 = self.evaluate_expression()
            self.check_compatibility(TokenType.NUMBER, expr1)
            expr1 = int(expr1.value)

            self.next_token()
            expr2 = self.evaluate_expression()
            self.check_compatibility(TokenType.NUMBER, expr2)
            expr2 = int(expr2.value)

            operator = self.next_token()

            if operator.type is not TokenType.DISTANCE_SEPARATOR:
                raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

            self.next_token()
            expr3 = self.evaluate_expression()
            self.check_compatibility(TokenType.NUMBER, expr3)
            expr3 = int(expr3.value)

            self.next_token()
            expr4 = self.evaluate_expression()
            self.check_compatibility(TokenType.NUMBER, expr4)
            expr4 = int(expr4.value)

            try:
                result = Value(TokenType.NUMBER, int((((expr4-expr2)**2)+((expr3-expr1)**2))**(1/2)))
            except ArithmeticError:
                raise InterpreterError(InterpreterError.INVALID_ARITHMETIC_OPERATION, self.token.line_no,
                                       self.get_current_line())
            return result
        # If the evaluation result is None (including the variable value), it is an expression error
        if value is None or (value is not None and type(value) is Value and value.value is None):
            raise InterpreterError(InterpreterError.INVALID_EXPRESSION, self.token.line_no, self.get_current_line())

        return value

    # Method to be called for INPUT statement
    # Checks this syntax: INPUT <variable_name>
    def input(self):
        variable = self.next_token()

        if variable.type is not TokenType.IDENTIFIER:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        input_value = input()

        typ = Lexer.get_type(input_value)
        # A floating-point value
        if typ == 1:
            raise InterpreterError(InterpreterError.INVALID_DATA_TYPE_INPUT, self.token.line_no,
                                   self.get_current_line())
        # An integer
        elif typ == 0:
            input_type = TokenType.NUMBER
        # A string
        else:
            input_type = TokenType.STRING

        self.assign_value_variable(variable.value, Value(input_type, input_value))

    # Method to be called for STORE statement
    # Checks this syntax: STORE <expression> IN <variable>
    def store(self):
        self.next_token()
        self.store_op_in_use = True
        expr = self.evaluate_expression()

        operator = self.token if self.token.type is TokenType.ASSIGN_VAR_KEY else self.next_token()

        # Not using IN operator
        if operator.type is not TokenType.ASSIGN_VAR_KEY:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        identifier = self.next_token()

        # Not an identifier
        if identifier.type is not TokenType.IDENTIFIER:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        self.assign_value_variable(identifier.value, expr)
        self.store_op_in_use = False

    # Method to be called for VARINT and VARSTR statements
    # Checks for these syntaxes:
    #   VARINT <variable_name>
    #   VARINT <variable_name> WITH <expression>
    #   VARSTR <variable_name>
    #   VARSTR <variable_name> WITH <expression>
    def assign(self):
        declaration_type = self.token
        identifier = self.next_token()
        value = None

        # Not an identifier
        if identifier.type is not TokenType.IDENTIFIER:
            raise InterpreterError(InterpreterError.INVALID_SYNTAX, self.token.line_no, self.get_current_line())

        operator = self.next_token()

        # Evaluate the expression if there is WITH operator
        if operator.type is TokenType.DECLARATION_ASSIGN_WITH_KEY:
            self.next_token()
            value = self.evaluate_expression()
            # No value evaluated from the expression
            if value is None:
                raise InterpreterError(InterpreterError.INVALID_EXPRESSION, self.token.line_no, self.get_current_line())
        # Use the corresponding literal value type depending on the Assignment operator used (VARINT/VARSTR)
        if declaration_type.type is TokenType.DECLARATION_INT:
            variable_type = TokenType.NUMBER
        else:
            variable_type = TokenType.STRING

        self.declare_variable(identifier.value, variable_type, value)

    # Method to be called for PRINT and PRINTLN statements
    # Check these syntaxes: PRINT <expression> ; PRINTLN <expression>
    def print(self, _end):
        self.next_token()
        value = self.evaluate_expression()
        # No value evaluated from the expression
        if value is None:
            raise InterpreterError(InterpreterError.INVALID_EXPRESSION, self.token.line_no, self.get_current_line())

        print(value.value, end=_end)

    # Handles arithmetic operations with only two parameters
    # Checks these syntaxes:
    #   ADD <expression1> <expression2>
    #   SUB <expression1> <expression2>
    #   MUL <expression1> <expression2>
    #   DIV <expression1> <expression2>
    #   MOD <expression1> <expression2>
    #   RAISE <expression> <exponent>
    #   ROOT <N> <expression>
    def two_operators_arithmetic(self):
        operator = self.token.type

        self.next_token()
        operand1 = self.evaluate_expression()
        self.check_compatibility(TokenType.NUMBER, operand1)

        operand1 = int(operand1.value)

        self.next_token()
        operand2 = self.evaluate_expression()
        self.check_compatibility(TokenType.NUMBER, operand2)
        operand2 = int(operand2.value)

        try:
            if operator == TokenType.BASIC_OPERATOR_ADD:
                return Value(TokenType.NUMBER, operand1 + operand2)
            if operator == TokenType.BASIC_OPERATOR_SUB:
                return Value(TokenType.NUMBER, operand1 - operand2)
            if operator == TokenType.BASIC_OPERATOR_MUL:
                return Value(TokenType.NUMBER, operand1 * operand2)
            if operator == TokenType.BASIC_OPERATOR_DIV:
                return Value(TokenType.NUMBER, int(operand1 / operand2))
            if operator == TokenType.BASIC_OPERATOR_MOD:
                return Value(TokenType.NUMBER, int(operand1 % operand2))
            if operator == TokenType.ADVANCED_OPERATOR_EXP:
                return Value(TokenType.NUMBER, int(operand1 ** operand2))
            if operator == TokenType.ADVANCED_OPERATOR_ROOT:
                return Value(TokenType.NUMBER, int(operand2 ** (1/float(operand1))))
        except ArithmeticError:
            raise InterpreterError(InterpreterError.INVALID_ARITHMETIC_OPERATION, self.token.line_no,
                                   self.get_current_line())

    # Returns the current line being evaluated
    def get_current_line(self): return self.lexer.line

    # Clears the current line
    def clear_current_line(self): self.lexer.line = ""

    # Checks if the programmar-defined identifiers are already declared
    def variable_exists(self, name): return name in self.variables

    # Creates a new variable entry to the variables dictionary
    def declare_variable(self, name, ident_type, value):
        if self.variable_exists(name):
            raise InterpreterError(InterpreterError.DUPLICATE_VARIABLE, self.token.line_no, self.get_current_line())

        self.check_compatibility(ident_type, value)

        # Get the Value instance's value property if value parameter is not None
        variable = Variable(name, ident_type, value.value if value is not None else value)
        self.variables[name] = variable

        if len(name) > self.longest_variable_length:
            self.longest_variable_length = len(name)

    # Sets a value to an existing variable
    def assign_value_variable(self, name, value):
        if not (self.variable_exists(name)):
            raise InterpreterError(InterpreterError.VARIABLE_NOT_DECLARED, self.token.line_no, self.get_current_line())

        variable = self.get_variable(name)

        self.check_compatibility(variable.type, value)

        variable.value = value.value
        self.variables[name] = variable

    # Checks if the value's type is the expected data type
    def check_compatibility(self, expected_data_type, value):
        if value is not None and expected_data_type is not value.type:
            raise InterpreterError(InterpreterError.INCOMPATIBLE_DATE_TYPE, self.token.line_no, self.get_current_line())

    # Returns the variable instance given the variable name
    def get_variable(self, name): return self.variables.get(name)

    # Returns the next token from the lexer
    def next_token(self):
        self.token = self.lexer.next_token()

        if self.token is not None:
            self.tokens.append(self.token)
            # Captures the previous statement for Invalid end of file error message
            if self.token.type is not TokenType.END_OF_STATEMENT and self.token.type is not TokenType.END_OF_FILE:
                self.prev_non_eos_line = self.get_current_line()
                self.prev_non_eos_lineno = self.token.line_no

        return self.token


# Main method executed when the script is called
def main():
    welcome_message = "========  INTERPOL INTERPRETER STARTED   ========\n"
    output_message = "================ INTERPOL OUTPUT ================\n"
    output_message_start = "----------------  OUTPUT START  ---------------->"
    output_message_end = "\n<----------------- OUTPUT END -------------------"
    token_list_header = "\n========= INTERPOL LEXEMES/TOKENS TABLE =========\n"
    token_list_columns = "LINE NO.  TOKENS                          LEXEMES"
    symbol_list_header = "\n================= SYMBOLS TABLE =================\n"
    symbol_list_columns = "VARIABLE NAME       TYPE        VALUE"
    termination_message = "\n======== INTERPOL INTERPRETER TERMINATED ========"

    print(welcome_message)

    file_path = input("Enter INTERPOL file (.ipol): ")
    # file_path = "input2.ipol"
    contents = None

    # Use the path relative to this script if path is not absolute
    if not os.path.isabs(file_path):
        file_path = pathlib.Path(str(pathlib.Path(__file__).parent.absolute()), file_path)

    # Check if the file extension is correct
    if not pathlib.Path(file_path).suffix == ".ipol":
        print(InterpreterError.INVALID_FILE)

    # Check if the file exists
    elif not os.path.isfile(file_path):
        print(InterpreterError.FILE_NOT_FOUND)

    # Check if the file has contents
    elif not os.path.getsize(file_path) > 0:
        print(InterpreterError.FILE_EMPTY)

    else:
        # Open the file in read mode using utf-8 encoding to avoid encoding errors
        file = open(file_path, 'r', encoding='utf-8')
        contents = file.read()

    if contents is not None:
        print(output_message)
        print(output_message_start)

        # Source code passed to lexer to be tokenized
        lexer = Lexer(contents)
        # lexer instance passed to parser, which processes each token
        parser = Parser(lexer)
        # Starts the parsing process
        parser.execute()

        print(output_message_end)

        # Display all tokens only if there are tokens available
        if len(parser.tokens) > 0:
            print(token_list_header)
            print(token_list_columns)

            for token in parser.tokens:
                print(str(token.line_no).ljust(10) + TokenType(token.type).name.ljust(32) + token.value)

        # Display all symbols only if there are symbols available
        if len(parser.variables) > 0:
            varname_ljust = 20

            # Adjusts the column width depending on the largest variable name
            if parser.longest_variable_length >= varname_ljust:
                varname_ljust = varname_ljust + (parser.longest_variable_length - varname_ljust + 1)
                symbol_list_columns = "VARIABLE NAME".ljust(varname_ljust) + "TYPE".ljust(12) + "VALUE"

            print(symbol_list_header)
            print(symbol_list_columns)

            for variable in parser.variables:
                var = parser.variables[variable]
                typ = "INTEGER" if var.type is TokenType.NUMBER else "STRING"
                val = "" if var.value is None else str(var.value)
                # Adjusts the column width depending on the largest variable name
                print(str(var.name).ljust(varname_ljust) + str(typ).ljust(12) + val)

    print(termination_message, end="")


# Execute INTERPOL program automatically if running the module itself
if __name__ == '__main__':
    main()
