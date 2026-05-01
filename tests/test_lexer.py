import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from afl_lang.lexer import Lexer, Token, TokenType


class TestLexerBasic:
    def test_empty_string(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_single_number(self):
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42
        assert tokens[1].type == TokenType.EOF

    def test_single_float(self):
        lexer = Lexer("3.14")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14

    def test_single_string_double_quotes(self):
        lexer = Lexer('"hello"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_single_string_single_quotes(self):
        lexer = Lexer("'hello'")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_identifier(self):
        lexer = Lexer("myVar")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "myVar"

    def test_underscore_identifier(self):
        lexer = Lexer("_private")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "_private"

    def test_boolean_true(self):
        lexer = Lexer("true")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BOOL
        assert tokens[0].value is True

    def test_boolean_false(self):
        lexer = Lexer("false")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BOOL
        assert tokens[0].value is False

    def test_null(self):
        lexer = Lexer("null")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NULL
        assert tokens[0].value is None


class TestLexerOperators:
    def test_arithmetic_operators(self):
        lexer = Lexer("+ - * / %")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT]

    def test_comparison_operators(self):
        lexer = Lexer("== != < <= > >=")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.EQEQ, TokenType.NEQ, TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE]

    def test_logical_operators(self):
        lexer = Lexer("&& ||")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.AND, TokenType.OR]

    def test_power_operator(self):
        lexer = Lexer("**")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STARSTAR

    def test_nullish_coalescing(self):
        lexer = Lexer("??")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.QQ

    def test_arrow(self):
        lexer = Lexer("->")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ARROW

    def test_assignment(self):
        lexer = Lexer("=")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.EQ

    def test_unary_minus(self):
        lexer = Lexer("-5")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.MINUS, TokenType.NUMBER]

    def test_not_operator(self):
        lexer = Lexer("not true")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NOT
        assert tokens[1].type == TokenType.BOOL


class TestLexerPunctuation:
    def test_braces(self):
        lexer = Lexer("{ }")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.LBRACE, TokenType.RBRACE]

    def test_parens(self):
        lexer = Lexer("( )")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.LPAREN, TokenType.RPAREN]

    def test_brackets(self):
        lexer = Lexer("[ ]")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.LBRACKET, TokenType.RBRACKET]

    def test_comma(self):
        lexer = Lexer(",")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.COMMA

    def test_colon(self):
        lexer = Lexer(":")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.COLON

    def test_dot(self):
        lexer = Lexer(".")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.DOT

    def test_question_mark(self):
        lexer = Lexer("?")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.EOF


class TestLexerKeywords:
    def test_if_keyword(self):
        lexer = Lexer("if")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IF

    def test_else_keyword(self):
        lexer = Lexer("else")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ELSE

    def test_elseif_keyword(self):
        lexer = Lexer("elseif")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ELSEIF

    def test_for_keyword(self):
        lexer = Lexer("for")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.FOR

    def test_in_keyword(self):
        lexer = Lexer("in")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IN

    def test_while_keyword(self):
        lexer = Lexer("while")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.WHILE

    def test_break_keyword(self):
        lexer = Lexer("break")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BREAK

    def test_continue_keyword(self):
        lexer = Lexer("continue")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.CONTINUE

    def test_function_keyword(self):
        lexer = Lexer("function")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.FUNCTION

    def test_return_keyword(self):
        lexer = Lexer("return")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.RETURN

    def test_try_catch_finally(self):
        lexer = Lexer("try catch finally")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.TRY, TokenType.CATCH, TokenType.FINALLY]

    def test_throw_keyword(self):
        lexer = Lexer("throw")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.THROW

    def test_let_keyword(self):
        lexer = Lexer("let")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LET

    def test_import_keyword(self):
        lexer = Lexer("import")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IMPORT

    def test_from_keyword(self):
        lexer = Lexer("from")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.FROM

    def test_export_keyword(self):
        lexer = Lexer("export")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.EXPORT

    def test_test_keyword(self):
        lexer = Lexer("test")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TEST

    def test_suite_keyword(self):
        lexer = Lexer("suite")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.SUITE

    def test_assert_keyword(self):
        lexer = Lexer("assert")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ASSERT

    def test_as_keyword(self):
        lexer = Lexer("as")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.AS

    def test_then_keyword(self):
        lexer = Lexer("then")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.THEN

    def test_async_keyword(self):
        lexer = Lexer("async")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ASYNC

    def test_await_keyword(self):
        lexer = Lexer("await")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.AWAIT

    def test_parallel_keyword(self):
        lexer = Lexer("parallel")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PARALLEL

    def test_wait_keyword(self):
        lexer = Lexer("wait")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.WAIT


class TestLexerStrings:
    def test_escape_sequences(self):
        lexer = Lexer('"hello\\nworld"')
        tokens = lexer.tokenize()
        assert tokens[0].value == "hello\nworld"

    def test_escape_tab(self):
        lexer = Lexer('"tab\\there"')
        tokens = lexer.tokenize()
        assert tokens[0].value == "tab\there"

    def test_escape_backslash(self):
        lexer = Lexer('"path\\\\to"')
        tokens = lexer.tokenize()
        assert tokens[0].value == "path\\to"

    def test_escape_quote_in_double(self):
        lexer = Lexer('"say \\"hi\\""')
        tokens = lexer.tokenize()
        assert tokens[0].value == 'say "hi"'

    def test_escape_quote_in_single(self):
        lexer = Lexer("'say \\'hi\\''")
        tokens = lexer.tokenize()
        assert tokens[0].value == "say 'hi'"

    def test_triple_double_quoted_string(self):
        lexer = Lexer('"""multi\nline"""')
        tokens = lexer.tokenize()
        assert tokens[0].value == "multi\nline"

    def test_triple_single_quoted_string(self):
        lexer = Lexer("'''multi\nline'''")
        tokens = lexer.tokenize()
        assert tokens[0].value == "multi\nline"

    def test_raw_string(self):
        lexer = Lexer('r"raw\\nstring"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "raw\\nstring"

    def test_empty_string(self):
        lexer = Lexer('""')
        tokens = lexer.tokenize()
        assert tokens[0].value == ""


class TestLexerComments:
    def test_single_line_comment(self):
        lexer = Lexer("42 # this is a comment")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert TokenType.NUMBER in types

    def test_comment_at_start(self):
        lexer = Lexer("# comment\n42")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF and t.type != TokenType.NEWLINE]
        assert types == [TokenType.NUMBER]


class TestLexerWhitespace:
    def test_newline_tokens(self):
        lexer = Lexer("1\n2")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        assert TokenType.NEWLINE in types

    def test_multiple_spaces(self):
        lexer = Lexer("1   2")
        tokens = lexer.tokenize()
        non_newline = [t for t in tokens if t.type not in (TokenType.EOF, TokenType.NEWLINE)]
        assert len(non_newline) == 2

    def test_tabs(self):
        lexer = Lexer("1\t2")
        tokens = lexer.tokenize()
        non_newline = [t for t in tokens if t.type not in (TokenType.EOF, TokenType.NEWLINE)]
        assert len(non_newline) == 2


class TestLexerExpressions:
    def test_arithmetic_expression(self):
        lexer = Lexer("1 + 2 * 3")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.NUMBER, TokenType.PLUS, TokenType.NUMBER, TokenType.STAR, TokenType.NUMBER]

    def test_function_call_tokens(self):
        lexer = Lexer("print(1, 2)")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.NUMBER, TokenType.COMMA, TokenType.NUMBER, TokenType.RPAREN]

    def test_attribute_access(self):
        lexer = Lexer("obj.method")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.IDENTIFIER, TokenType.DOT, TokenType.IDENTIFIER]

    def test_index_access(self):
        lexer = Lexer("arr[0]")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.IDENTIFIER, TokenType.LBRACKET, TokenType.NUMBER, TokenType.RBRACKET]

    def test_list_literal(self):
        lexer = Lexer("[1, 2, 3]")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.LBRACKET, TokenType.NUMBER, TokenType.COMMA, TokenType.NUMBER, TokenType.COMMA, TokenType.NUMBER, TokenType.RBRACKET]

    def test_dict_literal(self):
        lexer = Lexer('{"key": "value"}')
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.LBRACE, TokenType.STRING, TokenType.COLON, TokenType.STRING, TokenType.RBRACE]

    def test_ternary_question_colon(self):
        lexer = Lexer("a ? b : c")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert TokenType.IDENTIFIER in types
        assert TokenType.COLON in types


class TestLexerTestIdentifier:
    def test_test_dot_is_identifier(self):
        lexer = Lexer("test.run()")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "test"
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "run"

    def test_test_standalone_is_keyword(self):
        lexer = Lexer('test "my test" {}')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TEST


class TestLexerNumbers:
    def test_zero(self):
        lexer = Lexer("0")
        tokens = lexer.tokenize()
        assert tokens[0].value == 0
        assert isinstance(tokens[0].value, int)

    def test_large_integer(self):
        lexer = Lexer("123456789")
        tokens = lexer.tokenize()
        assert tokens[0].value == 123456789

    def test_negative_number_tokens(self):
        lexer = Lexer("-42")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert types == [TokenType.MINUS, TokenType.NUMBER]

    def test_float_no_leading_zero(self):
        lexer = Lexer(".5")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.DOT
        assert tokens[1].type == TokenType.NUMBER


class TestLexerLineInfo:
    def test_line_tracking(self):
        lexer = Lexer("1\n2\n3")
        tokens = lexer.tokenize()
        num_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        assert num_tokens[0].line == 1
        assert num_tokens[1].line == 2
        assert num_tokens[2].line == 3

    def test_column_tracking(self):
        lexer = Lexer("   abc")
        tokens = lexer.tokenize()
        assert tokens[0].col == 7


class TestLexerUnknownChar:
    def test_unknown_character_ignored(self):
        lexer = Lexer("@")
        tokens = lexer.tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 0

    def test_multiple_unknown_chars(self):
        lexer = Lexer("@#$")
        tokens = lexer.tokenize()
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        assert len(non_eof) == 0
