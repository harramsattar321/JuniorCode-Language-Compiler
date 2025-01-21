import re
from dataclasses import dataclass
from typing import Any, List, Optional, Dict, Union

# ==========================
# LEXER (Tokenizer)
# ==========================
@dataclass
class Token:
    type: str
    value: Any
    line: int
    column: int

class Lexer:
    KEYWORDS = ["show", "var", "ask", "if", "else", "repeat", "to", "loop"]
    OPERATORS = {
        '=': 'ASSIGN',
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'MULTIPLY',
        '/': 'DIVIDE',
        '<': 'LESS',
        '>': 'GREATER',
        '<=': 'LESS_EQUAL',
        '>=': 'GREATER_EQUAL',
        '==': 'EQUALS',
        '!=': 'NOT_EQUALS',
        '{': 'LBRACE',
        '}': 'RBRACE'
    }

    def __init__(self, code: str):
        self.code = code
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        self.current_pos = 0

    def tokenize(self) -> List[Token]:
        while self.current_pos < len(self.code):
            char = self.code[self.current_pos]
            
            # Skip whitespace
            if char.isspace():
                if char == '\n':
                    self.current_line += 1
                    self.current_column = 1
                else:
                    self.current_column += 1
                self.current_pos += 1
                continue

            # Handle keywords and identifiers
            if char.isalpha():
                self.tokenize_word()
                continue

            # Handle strings
            if char in '"\'':
                self.tokenize_string()
                continue

            # Handle numbers
            if char.isdigit():
                self.tokenize_number()
                continue

            # Handle multi-character operators
            if char in '<>=!':
                self.tokenize_comparison()
                continue

            # Handle single-character operators
            if char in self.OPERATORS:
                self.tokenize_operator()
                continue

            # Unrecognized character
            self.raise_error(f"Oops! I found a character I don't understand: '{char}'")

        return self.tokens

    def tokenize_word(self):
        word = ""
        start_col = self.current_column

        while self.current_pos < len(self.code) and (self.code[self.current_pos].isalnum() or self.code[self.current_pos] == '_'):
            word += self.code[self.current_pos]
            self.current_pos += 1
            self.current_column += 1

        if word in self.KEYWORDS:
            self.tokens.append(Token('KEYWORD', word, self.current_line, start_col))
        else:
            self.tokens.append(Token('IDENTIFIER', word, self.current_line, start_col))

    def tokenize_string(self):
        quote = self.code[self.current_pos]
        start_col = self.current_column
        self.current_pos += 1
        self.current_column += 1
        string_value = ""

        while self.current_pos < len(self.code):
            char = self.code[self.current_pos]
            if char == quote:
                self.current_pos += 1
                self.current_column += 1
                self.tokens.append(Token('STRING', string_value, self.current_line, start_col))
                return
            if char == '\n':
                self.raise_error("Oops! You forgot to close your string with a quotation mark!")
            string_value += char
            self.current_pos += 1
            self.current_column += 1

        self.raise_error("Oops! You need to close your string with a quotation mark!")

    def tokenize_number(self):
        number = ""
        start_col = self.current_column

        while self.current_pos < len(self.code) and (self.code[self.current_pos].isdigit() or self.code[self.current_pos] == '.'):
            number += self.code[self.current_pos]
            self.current_pos += 1
            self.current_column += 1

        try:
            value = int(number) if '.' not in number else float(number)
            self.tokens.append(Token('NUMBER', value, self.current_line, start_col))
        except ValueError:
            self.raise_error(f"Oops! '{number}' isn't a valid number!")

    def tokenize_comparison(self):
        start_col = self.current_column
        operator = self.code[self.current_pos]
        next_char = self.code[self.current_pos + 1] if self.current_pos + 1 < len(self.code) else ''
        
        if next_char == '=':
            operator += next_char
            self.current_pos += 2
            self.current_column += 2
        else:
            self.current_pos += 1
            self.current_column += 1

        token_type = self.OPERATORS.get(operator)
        if token_type:
            self.tokens.append(Token(token_type, operator, self.current_line, start_col))
        else:
            self.raise_error(f"Oops! I don't understand this operator: '{operator}'")

    def tokenize_operator(self):
        start_col = self.current_column
        operator = self.code[self.current_pos]
        self.current_pos += 1
        self.current_column += 1
        token_type = self.OPERATORS.get(operator)
        if token_type:
            self.tokens.append(Token(token_type, operator, self.current_line, start_col))
        else:
            self.raise_error(f"Oops! I don't understand this operator: '{operator}'")

    def raise_error(self, message: str):
        raise SyntaxError(f"{message}\nLine {self.current_line}, Column {self.current_column}")

# ==========================
# PARSER
# ==========================
class ASTNode:
    pass

class ShowNode(ASTNode):
    def __init__(self, value: Any):
        self.value = value

class VarNode(ASTNode):
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

class IdentifierNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

class BinaryOpNode(ASTNode):
    def __init__(self, left: Any, operator: str, right: Any):
        self.left = left
        self.operator = operator
        self.right = right

class IfNode(ASTNode):
    def __init__(self, condition: Any, if_body: List[ASTNode], else_body: Optional[List[ASTNode]] = None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class RepeatNode(ASTNode):
    def __init__(self, var_name: str, start: int, end: int, body: List[ASTNode]):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.body = body

class LoopNode(ASTNode):
    def __init__(self, condition: Any, body: List[ASTNode]):
        self.condition = condition
        self.body = body

class AskNode(ASTNode):
    def __init__(self, prompt: str):
        self.prompt = prompt

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[ASTNode]:
        statements = []
        while not self.is_at_end():
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> ASTNode:
        token = self.peek()
        
        if token.type == 'KEYWORD':
            if token.value == 'show':
                return self.parse_show()
            elif token.value == 'var':
                return self.parse_var()
            elif token.value == 'if':
                return self.parse_if()
            elif token.value == 'repeat':
                return self.parse_repeat()
            elif token.value == 'loop':
                return self.parse_loop()
            
        self.raise_error("Oops! I was expecting a statement here!")

    def parse_show(self) -> ShowNode:
        self.consume('KEYWORD', 'show')
        expr = self.parse_expression()
        return ShowNode(expr)

    def parse_var(self) -> VarNode:
        self.consume('KEYWORD', 'var')
        name_token = self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        
        if self.peek().type == 'KEYWORD' and self.peek().value == 'ask':
            self.advance()  # consume 'ask'
            prompt_token = self.consume('STRING')
            return VarNode(name_token.value, AskNode(prompt_token.value))
        
        value = self.parse_expression()
        return VarNode(name_token.value, value)

    def parse_if(self) -> IfNode:
        self.consume('KEYWORD', 'if')
        condition = self.parse_expression()
        self.consume('LBRACE')
        
        if_body = []
        while not self.is_at_end() and self.peek().type != 'RBRACE':
            if_body.append(self.parse_statement())
        self.consume('RBRACE')
        
        else_body = None
        if not self.is_at_end() and self.peek().type == 'KEYWORD' and self.peek().value == 'else':
            self.advance()  # consume 'else'
            self.consume('LBRACE')
            else_body = []
            while not self.is_at_end() and self.peek().type != 'RBRACE':
                else_body.append(self.parse_statement())
            self.consume('RBRACE')
            
        return IfNode(condition, if_body, else_body)

    def parse_repeat(self) -> RepeatNode:
        self.consume('KEYWORD', 'repeat')
        var_name = self.consume('IDENTIFIER').value
        start = self.consume('NUMBER').value
        self.consume('KEYWORD', 'to')
        end = self.consume('NUMBER').value
        self.consume('LBRACE')
        
        body = []
        while not self.is_at_end() and self.peek().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        
        return RepeatNode(var_name, start, end, body)

    def parse_loop(self) -> LoopNode:
        self.consume('KEYWORD', 'loop')
        condition = self.parse_expression()
        self.consume('LBRACE')
        
        body = []
        while not self.is_at_end() and self.peek().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        
        return LoopNode(condition, body)

    def parse_expression(self) -> Any:
        return self.parse_comparison()

    def parse_comparison(self) -> Any:
        expr = self.parse_arithmetic()
        
        while (not self.is_at_end() and self.peek().type in 
               ['EQUALS', 'NOT_EQUALS', 'LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL']):
            operator = self.advance()
            right = self.parse_arithmetic()
            expr = BinaryOpNode(expr, operator.type, right)
            
        return expr

    def parse_arithmetic(self) -> Any:
        expr = self.parse_term()
        
        while not self.is_at_end() and self.peek().type in ['PLUS', 'MINUS']:
            operator = self.advance()
            right = self.parse_term()
            expr = BinaryOpNode(expr, operator.type, right)
            
        return expr

    def parse_term(self) -> Any:
        expr = self.parse_primary()
        
        while not self.is_at_end() and self.peek().type in ['MULTIPLY', 'DIVIDE']:
            operator = self.advance()
            right = self.parse_primary()
            expr = BinaryOpNode(expr, operator.type, right)
            
        return expr

    def parse_primary(self) -> Any:
        token = self.advance()
        
        if token.type in ['NUMBER', 'STRING']:
            return token.value
        elif token.type == 'IDENTIFIER':
            return IdentifierNode(token.value)
            
        self.raise_error("Oops! I was expecting a value here!")

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def peek(self) -> Token:
        if self.is_at_end():
            raise SyntaxError("Oops! The program ended before I expected!")
        return self.tokens[self.current]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def consume(self, type: str, value: Optional[str] = None) -> Token:
        if self.is_at_end():
            self.raise_error(f"Oops! I was expecting {type} but the program ended!")
            
        current = self.peek()
        if current.type != type:
            self.raise_error(f"Oops! I was expecting {type} but found {current.type}!")
            
        if value is not None and current.value != value:
            self.raise_error(f"Oops! I was expecting '{value}' but found '{current.value}'!")
            
        return self.advance()

    def raise_error(self, message: str):
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            raise SyntaxError(f"{message}\nLine {token.line}, Column {token.column}")
        raise SyntaxError(message)

# ==========================
# INTERPRETER
# ==========================
class Interpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}

    def interpret(self, nodes: List[ASTNode]):
        result = None
        for node in nodes:
            result = self.evaluate(node)
        return result

    def evaluate(self, node: ASTNode) -> Any:
        if isinstance(node, ShowNode):
            value = self.evaluate(node.value)
            print(value)
        elif isinstance(node, VarNode):
            value = self.evaluate(node.value)
            self.variables[node.name] = value
        elif isinstance(node, IdentifierNode):
            if node.name not in self.variables:
                raise NameError(f"Oops! I don't know about any variable named '{node.name}'")
            return self.variables[node.name]
        elif isinstance(node, BinaryOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            return self.evaluate_operation(left, node.operator, right)
        elif isinstance(node, IfNode):
            condition_value = self.evaluate(node.condition)
            if condition_value:
                for statement in node.if_body:
                    self.evaluate(statement)
            elif node.else_body:
                for statement in node.else_body:
                    self.evaluate(statement)
        elif isinstance(node, RepeatNode):
            for i in range(node.start, node.end + 1):
                self.variables[node.var_name] = i
                for statement in node.body:
                    self.evaluate(statement)
        elif isinstance(node, LoopNode):
            while self.evaluate(node.condition):
                for statement in node.body:
                    self.evaluate(statement)
        elif isinstance(node, AskNode):
            return input(node.prompt + " ")
        else:
            return node

    def evaluate_operation(self, left: Any, operator: str, right: Any) -> Any:
        # First convert operands to strings if either operand is a string and we're doing addition
        if operator == 'PLUS' and (isinstance(left, str) or isinstance(right, str)):
            return str(left) + str(right)
            
        # For all other operations, proceed with normal arithmetic
        if operator == 'PLUS':
            return left + right
        elif operator == 'MINUS':
            return left - right
        elif operator == 'MULTIPLY':
            return left * right
        elif operator == 'DIVIDE':
            if right == 0:
                raise ValueError("Oops! You can't divide by zero!")
            return left / right
        elif operator == 'EQUALS':
            return left == right
        elif operator == 'NOT_EQUALS':
            return left != right
        elif operator == 'LESS':
            return left < right
        elif operator == 'GREATER':
            return left > right
        elif operator == 'LESS_EQUAL':
            return left <= right
        elif operator == 'GREATER_EQUAL':
            return left >= right
        else:
            raise ValueError(f"Oops! I don't know how to do this operation: {operator}")

# ==========================
# MAIN FUNCTION
# ==========================
def run_junior_code():
    print("Welcome to JuniorCode!")
    print("Type your code below (type 'END' on a new line to finish):")
    
    code_lines = []
    while True:
        try:
            line = input("> ")
            if line.strip().upper() == "END":
                break
            code_lines.append(line)
        except KeyboardInterrupt:
            print("\nBye bye!")
            return
    
    code = "\n".join(code_lines)
    
    try:
        # Step 1: Tokenize the code
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Step 2: Parse the tokens into an AST
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Step 3: Interpret the AST
        print("\nOutput:")
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except SyntaxError as e:
        print(f"🚨 {str(e)}")
    except Exception as e:
        print(f"🤔 Oops! Something went wrong: {str(e)}")

# Example usage


if __name__ == "__main__":
    run_junior_code()