import re
from dataclasses import dataclass
from typing import Any
from enum import Enum


class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOL = "BOOL"
    NULL = "NULL"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    COLON = "COLON"
    DOT = "DOT"
    QQ = "QQ"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    PERCENT = "PERCENT"
    STARSTAR = "STARSTAR"
    EQ = "EQ"
    EQEQ = "EQEQ"
    NEQ = "NEQ"
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"
    ARROW = "ARROW"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    QUESTION = "QUESTION"
    THEN = "THEN"
    ASSERT = "ASSERT"
    AS = "AS"
    FROM = "FROM"
    ASYNC = "ASYNC"
    AWAIT = "AWAIT"
    PARALLEL = "PARALLEL"
    WAIT = "WAIT"
    IF = "IF"
    ELSE = "ELSE"
    ELSEIF = "ELSEIF"
    FOR = "FOR"
    IN = "IN"
    WHILE = "WHILE"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"
    LET = "LET"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    TEST = "TEST"
    SUITE = "SUITE"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    col: int = 1


class Lexer:
    KEYWORDS = {
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "elseif": TokenType.ELSEIF,
        "for": TokenType.FOR,
        "in": TokenType.IN,
        "while": TokenType.WHILE,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE,
        "function": TokenType.FUNCTION,
        "return": TokenType.RETURN,
        "try": TokenType.TRY,
        "catch": TokenType.CATCH,
        "finally": TokenType.FINALLY,
        "throw": TokenType.THROW,
        "let": TokenType.LET,
        "import": TokenType.IMPORT,
        "from": TokenType.FROM,
        "export": TokenType.EXPORT,
        "test": TokenType.TEST,
        "suite": TokenType.SUITE,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "null": TokenType.NULL,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        "then": TokenType.THEN,
        "assert": TokenType.ASSERT,
        "as": TokenType.AS,
        "async": TokenType.ASYNC,
        "await": TokenType.AWAIT,
        "parallel": TokenType.PARALLEL,
        "wait": TokenType.WAIT,
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.current_char = self.source[0] if self.source else None

    def advance(self):
        if self.current_char == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        self.current_char = self.source[self.pos] if self.pos < len(self.source) else None

    def peek(self, offset=1):
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            if self.current_char == "\n":
                self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.col))
            self.advance()

    def skip_comment(self):
        while self.current_char and self.current_char != "\n":
            self.advance()

    def read_number(self):
        num_str = ""
        has_dot = False
        while self.current_char and (self.current_char.isdigit() or self.current_char == "."):
            if self.current_char == ".":
                if has_dot:
                    break
                has_dot = True
            num_str += self.current_char
            self.advance()
        return float(num_str) if "." in num_str else int(num_str)

    def read_string(self, raw=False):
        quote = self.current_char
        self.advance()
        # Check for triple-quoted strings """ or '''
        if self.current_char == quote and self.peek() == quote:
            self.advance()  # skip second quote
            self.advance()  # skip third quote
            string_val = ""
            while self.current_char:
                if self.current_char == "\\" and self.peek() == quote:
                    self.advance()
                    self.advance()
                    string_val += quote
                elif self.current_char == quote and self.peek() == quote and self.peek(2) == quote:
                    self.advance()
                    self.advance()
                    self.advance()
                    return string_val
                else:
                    string_val += self.current_char
                    self.advance()
            return string_val
        # Single/double quoted strings
        string_val = ""
        escape_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'"}
        while self.current_char and self.current_char != quote:
            if self.current_char == "\\" and self.peek() and not raw:
                self.advance()
                string_val += escape_map.get(self.current_char, self.current_char)
            else:
                string_val += self.current_char
            self.advance()
        self.advance()
        return string_val

    def read_identifier(self):
        ident = ""
        while self.current_char and (self.current_char.isalnum() or self.current_char == "_"):
            ident += self.current_char
            self.advance()
        return ident

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()
            if not self.current_char:
                break
            if self.current_char == "#":
                self.skip_comment()
                continue
            if self.current_char == '"' or self.current_char == "'":
                val = self.read_string()
                self.tokens.append(Token(TokenType.STRING, val, self.line, self.col))
                continue
            if self.current_char.isdigit():
                num = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, num, self.line, self.col))
                continue
            if self.current_char.isalpha() or self.current_char == "_":
                # Check for raw strings: r"..." or r'...'
                if self.current_char in ('r', 'R') and self.peek() in ('"', "'"):
                    self.advance()
                    val = self.read_string(raw=True)
                    self.tokens.append(Token(TokenType.STRING, val, self.line, self.col))
                    continue
                ident = self.read_identifier()
                token_type = self.KEYWORDS.get(ident.lower(), TokenType.IDENTIFIER)
                if token_type == TokenType.TEST:
                    saved_pos = self.pos
                    saved_char = self.current_char
                    while self.current_char and self.current_char in [" ", "\t"]:
                        self.advance()
                    if self.current_char == ".":
                        token_type = TokenType.IDENTIFIER
                    else:
                        self.pos = saved_pos
                        self.current_char = saved_char
                if token_type == TokenType.TRUE:
                    self.tokens.append(Token(TokenType.BOOL, True, self.line, self.col))
                elif token_type == TokenType.FALSE:
                    self.tokens.append(Token(TokenType.BOOL, False, self.line, self.col))
                elif token_type == TokenType.NULL:
                    self.tokens.append(Token(TokenType.NULL, None, self.line, self.col))
                else:
                    self.tokens.append(Token(token_type, ident, self.line, self.col))
                continue

            char = self.current_char
            two_char = char + (self.peek() or "")
            two_char_map = {
                "==": TokenType.EQEQ,
                "!=": TokenType.NEQ,
                "<=": TokenType.LTE,
                ">=": TokenType.GTE,
                "&&": TokenType.AND,
                "||": TokenType.OR,
                "**": TokenType.STARSTAR,
                "->": TokenType.ARROW,
                "??": TokenType.QQ,
            }
            
            char_map = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "%": TokenType.PERCENT,
                "=": TokenType.EQ,
                "<": TokenType.LT,
                ">": TokenType.GT,
            }

            if two_char in two_char_map:
                self.tokens.append(Token(two_char_map[two_char], two_char, self.line, self.col))
                self.advance()
                self.advance()
            elif char in char_map:
                self.tokens.append(Token(char_map[char], char, self.line, self.col))
                self.advance()
            elif char == "{":
                self.tokens.append(Token(TokenType.LBRACE, char, self.line, self.col))
                self.advance()
            elif char == "}":
                self.tokens.append(Token(TokenType.RBRACE, char, self.line, self.col))
                self.advance()
            elif char == "(":
                self.tokens.append(Token(TokenType.LPAREN, char, self.line, self.col))
                self.advance()
            elif char == ")":
                self.tokens.append(Token(TokenType.RPAREN, char, self.line, self.col))
                self.advance()
            elif char == "[":
                self.tokens.append(Token(TokenType.LBRACKET, char, self.line, self.col))
                self.advance()
            elif char == "]":
                self.tokens.append(Token(TokenType.RBRACKET, char, self.line, self.col))
                self.advance()
            elif char == ",":
                self.tokens.append(Token(TokenType.COMMA, char, self.line, self.col))
                self.advance()
            elif char == ":":
                self.tokens.append(Token(TokenType.COLON, char, self.line, self.col))
                self.advance()
            elif char == ".":
                self.tokens.append(Token(TokenType.DOT, char, self.line, self.col))
                self.advance()
            else:
                self.advance()

        self.tokens.append(Token(TokenType.EOF, None, self.line))
        return self.tokens