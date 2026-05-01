import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from afl_lang.lexer import Lexer, TokenType
from afl_lang.parser import Parser
from afl_lang.nodes import (
    ProgramNode, NumberNode, StringNode, BoolNode, NullNode, IdentifierNode,
    ListNode, DictNode, BinaryOpNode, UnaryOpNode, TernaryNode, IfNode, ForNode,
    WhileNode, FunctionDefNode, FunctionCallNode, CallNode, ReturnNode, BreakNode,
    ContinueNode, TryNode, ThrowNode, ImportNode, TestNode, SuiteNode, BlockNode,
    VarNode, AttributeNode, AssertNode, FromImportNode, ExportNode,
    AsyncNode, AwaitNode, ParallelNode, WaitNode, IndexNode,
    AssignNode, SetItemNode
)


def parse(source):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


class TestParserLiterals:
    def test_number(self):
        ast = parse("42")
        assert isinstance(ast, ProgramNode)
        assert isinstance(ast.statements[0], NumberNode)
        assert ast.statements[0].value == 42

    def test_float(self):
        ast = parse("3.14")
        assert isinstance(ast.statements[0], NumberNode)
        assert ast.statements[0].value == 3.14

    def test_string(self):
        ast = parse('"hello"')
        assert isinstance(ast.statements[0], StringNode)
        assert ast.statements[0].value == "hello"

    def test_true(self):
        ast = parse("true")
        assert isinstance(ast.statements[0], BoolNode)
        assert ast.statements[0].value is True

    def test_false(self):
        ast = parse("false")
        assert isinstance(ast.statements[0], BoolNode)
        assert ast.statements[0].value is False

    def test_null(self):
        ast = parse("null")
        assert isinstance(ast.statements[0], NullNode)

    def test_empty_program(self):
        ast = parse("")
        assert isinstance(ast, ProgramNode)
        assert len(ast.statements) == 0


class TestParserVariables:
    def test_var_declaration(self):
        ast = parse("let x = 10")
        assert isinstance(ast.statements[0], VarNode)
        assert ast.statements[0].name == "x"
        assert isinstance(ast.statements[0].value, NumberNode)
        assert ast.statements[0].value.value == 10

    def test_var_with_type(self):
        ast = parse("let x: string = 'hello'")
        assert ast.statements[0].name == "x"
        assert ast.statements[0].type_name == "string"

    def test_var_with_identifier_value(self):
        ast = parse("let x = y")
        assert isinstance(ast.statements[0].value, IdentifierNode)
        assert ast.statements[0].value.name == "y"


class TestParserOperators:
    def test_addition(self):
        ast = parse("1 + 2")
        assert isinstance(ast.statements[0], BinaryOpNode)
        assert ast.statements[0].op == "+"

    def test_subtraction(self):
        ast = parse("5 - 3")
        assert ast.statements[0].op == "-"

    def test_multiplication(self):
        ast = parse("2 * 3")
        assert ast.statements[0].op == "*"

    def test_division(self):
        ast = parse("10 / 2")
        assert ast.statements[0].op == "/"

    def test_modulo(self):
        ast = parse("10 % 3")
        assert ast.statements[0].op == "%"

    def test_power(self):
        ast = parse("2 ** 3")
        assert ast.statements[0].op == "**"

    def test_equality(self):
        ast = parse("a == b")
        assert ast.statements[0].op == "=="

    def test_not_equal(self):
        ast = parse("a != b")
        assert ast.statements[0].op == "!="

    def test_less_than(self):
        ast = parse("a < b")
        assert ast.statements[0].op == "<"

    def test_less_equal(self):
        ast = parse("a <= b")
        assert ast.statements[0].op == "<="

    def test_greater_than(self):
        ast = parse("a > b")
        assert ast.statements[0].op == ">"

    def test_greater_equal(self):
        ast = parse("a >= b")
        assert ast.statements[0].op == ">="

    def test_and(self):
        ast = parse("a && b")
        assert ast.statements[0].op == "and"

    def test_or(self):
        ast = parse("a || b")
        assert ast.statements[0].op == "or"

    def test_nullish_coalescing(self):
        ast = parse("a ?? b")
        assert ast.statements[0].op == "??"

    def test_in_operator(self):
        ast = parse("x in list")
        assert ast.statements[0].op == "in"

    def test_unary_minus(self):
        ast = parse("-x")
        assert isinstance(ast.statements[0], UnaryOpNode)
        assert ast.statements[0].op == "-"

    def test_not_operator(self):
        ast = parse("not x")
        assert isinstance(ast.statements[0], UnaryOpNode)
        assert ast.statements[0].op == "not"


class TestParserTernary:
    def test_ternary_question_colon(self):
        ast = parse("? true then 1 else 2")
        assert isinstance(ast.statements[0], TernaryNode)


class TestParserConditionals:
    def test_if_statement(self):
        ast = parse("if x { let y = 1 }")
        assert isinstance(ast.statements[0], IfNode)
        assert isinstance(ast.statements[0].condition, IdentifierNode)
        assert len(ast.statements[0].elseif_branches) == 0
        assert ast.statements[0].else_branch is None

    def test_if_else(self):
        ast = parse("if x { let a = 1 } else { let b = 2 }")
        assert ast.statements[0].else_branch is not None

    def test_if_elseif(self):
        ast = parse("if x { let a = 1 } elseif y { let b = 2 }")
        assert len(ast.statements[0].elseif_branches) == 1

    def test_if_elseif_else(self):
        ast = parse("if x { let a = 1 } elseif y { let b = 2 } else { let c = 3 }")
        assert len(ast.statements[0].elseif_branches) == 1
        assert ast.statements[0].else_branch is not None


class TestParserLoops:
    def test_for_loop(self):
        ast = parse("for i in range(10) { print(i) }")
        assert isinstance(ast.statements[0], ForNode)
        assert ast.statements[0].variable == "i"

    def test_while_loop(self):
        ast = parse("while x < 10 { let x = x + 1 }")
        assert isinstance(ast.statements[0], WhileNode)

    def test_break(self):
        ast = parse("break")
        assert isinstance(ast.statements[0], BreakNode)

    def test_continue(self):
        ast = parse("continue")
        assert isinstance(ast.statements[0], ContinueNode)


class TestParserFunctions:
    def test_function_definition(self):
        ast = parse("function add(a, b) { return a + b }")
        assert isinstance(ast.statements[0], FunctionDefNode)
        assert ast.statements[0].name == "add"
        assert len(ast.statements[0].params) == 2
        assert ast.statements[0].params[0][0] == "a"
        assert ast.statements[0].params[1][0] == "b"

    def test_function_with_defaults(self):
        ast = parse("function greet(name = 'world') { print(name) }")
        assert ast.statements[0].params[0][2] is not None

    def test_function_with_return_type(self):
        ast = parse("function add(a, b) -> number { return a + b }")
        assert ast.statements[0].return_type == "number"

    def test_function_with_typed_params(self):
        ast = parse("function add(a: number, b: number) { return a + b }")
        assert ast.statements[0].params[0][1] == "number"
        assert ast.statements[0].params[1][1] == "number"

    def test_function_call(self):
        ast = parse("print(1, 2)")
        assert isinstance(ast.statements[0], FunctionCallNode)
        assert isinstance(ast.statements[0].name, IdentifierNode)
        assert ast.statements[0].name.name == "print"
        assert len(ast.statements[0].args) == 2

    def test_function_call_with_kwargs(self):
        ast = parse("foo(a = 1, b = 2)")
        assert isinstance(ast.statements[0], FunctionCallNode)
        assert "a" in ast.statements[0].kwargs
        assert "b" in ast.statements[0].kwargs

    def test_return_statement(self):
        ast = parse("return 42")
        assert isinstance(ast.statements[0], ReturnNode)
        assert isinstance(ast.statements[0].value, NumberNode)

    def test_return_no_value(self):
        ast = parse("function f() { return }")
        func = ast.statements[0]
        assert isinstance(func.body.statements[0], ReturnNode)
        assert isinstance(func.body.statements[0].value, NullNode)


class TestParserAttributeAndIndex:
    def test_attribute_access(self):
        ast = parse("obj.method")
        assert isinstance(ast.statements[0], AttributeNode)
        assert ast.statements[0].attribute == "method"

    def test_index_access(self):
        ast = parse("arr[0]")
        assert isinstance(ast.statements[0], IndexNode)
        assert isinstance(ast.statements[0].index, NumberNode)

    def test_method_call(self):
        ast = parse("obj.method(1, 2)")
        assert isinstance(ast.statements[0], CallNode)
        assert isinstance(ast.statements[0].callee, AttributeNode)

    def test_chained_attribute(self):
        ast = parse("a.b.c")
        assert isinstance(ast.statements[0], AttributeNode)


class TestParserAssignment:
    def test_simple_assignment(self):
        ast = parse("x = 10")
        assert isinstance(ast.statements[0], AssignNode)
        assert isinstance(ast.statements[0].target, IdentifierNode)
        assert ast.statements[0].target.name == "x"

    def test_setitem_assignment(self):
        ast = parse("arr[0] = 10")
        assert isinstance(ast.statements[0], SetItemNode)


class TestParserListsAndDicts:
    def test_list_literal(self):
        ast = parse("[1, 2, 3]")
        assert isinstance(ast.statements[0], ListNode)
        assert len(ast.statements[0].elements) == 3

    def test_empty_list(self):
        ast = parse("[]")
        assert isinstance(ast.statements[0], ListNode)
        assert len(ast.statements[0].elements) == 0

    def test_dict_literal(self):
        ast = parse('{"key": "value"}')
        assert isinstance(ast.statements[0], DictNode)
        assert "key" in ast.statements[0].pairs

    def test_empty_dict(self):
        ast = parse("{}")
        assert isinstance(ast.statements[0], DictNode)
        assert len(ast.statements[0].pairs) == 0

    def test_nested_list(self):
        ast = parse("[[1, 2], [3, 4]]")
        assert isinstance(ast.statements[0], ListNode)
        assert len(ast.statements[0].elements) == 2
        assert isinstance(ast.statements[0].elements[0], ListNode)


class TestParserErrorHandling:
    def test_try_catch(self):
        ast = parse("try { let x = 1 } catch e { print(e) }")
        assert isinstance(ast.statements[0], TryNode)
        assert ast.statements[0].catch_body is not None
        assert ast.statements[0].finally_body is None

    def test_try_finally(self):
        ast = parse("try { let x = 1 } finally { print('done') }")
        assert isinstance(ast.statements[0], TryNode)
        assert ast.statements[0].catch_body is None
        assert ast.statements[0].finally_body is not None

    def test_try_catch_finally(self):
        ast = parse("try { let x = 1 } catch e { print(e) } finally { print('done') }")
        node = ast.statements[0]
        assert node.catch_body is not None
        assert node.finally_body is not None

    def test_throw(self):
        ast = parse("throw 'error'")
        assert isinstance(ast.statements[0], ThrowNode)
        assert isinstance(ast.statements[0].value, StringNode)

    def test_assert(self):
        ast = parse("assert x == 1")
        assert isinstance(ast.statements[0], AssertNode)

    def test_assert_with_message(self):
        ast = parse('assert x == 1, "x should be 1"')
        assert ast.statements[0].message == "x should be 1"


class TestParserTestAndSuite:
    def test_test_statement(self):
        ast = parse('test "my test" { assert true }')
        assert isinstance(ast.statements[0], TestNode)
        assert ast.statements[0].name == "my test"

    def test_suite_statement(self):
        ast = parse('suite "my suite" { test "t1" { assert true } }')
        assert isinstance(ast.statements[0], SuiteNode)
        assert ast.statements[0].name == "my suite"
        assert len(ast.statements[0].tests) == 1


class TestParserImportExport:
    def test_import(self):
        ast = parse('import "module.agent"')
        assert isinstance(ast.statements[0], ImportNode)
        assert ast.statements[0].path == "module.agent"

    def test_import_as(self):
        ast = parse('import "module.agent" as mod')
        assert ast.statements[0].path == "module.agent"
        assert ast.statements[0].alias == "mod"

    def test_from_import(self):
        ast = parse('from "module.agent" import foo, bar')
        assert isinstance(ast.statements[0], FromImportNode)
        assert ast.statements[0].path == "module.agent"
        assert ast.statements[0].names == ["foo", "bar"]

    def test_export_function(self):
        ast = parse("export function foo() { return 1 }")
        assert isinstance(ast.statements[0], FunctionDefNode)
        assert ast.statements[0].name == "foo"

    def test_export_variable(self):
        ast = parse("export let x = 10")
        assert isinstance(ast.statements[0], VarNode)
        assert ast.statements[0].name == "x"


class TestParserAsync:
    def test_async_block(self):
        ast = parse("async { let x = 1 }")
        assert isinstance(ast.statements[0], AsyncNode)

    def test_await_expression(self):
        ast = parse("await foo()")
        assert isinstance(ast.statements[0], AwaitNode)

    def test_parallel_block(self):
        ast = parse("parallel { let a = 1 let b = 2 }")
        assert isinstance(ast.statements[0], ParallelNode)
        assert len(ast.statements[0].statements) == 2

    def test_wait_all(self):
        ast = parse("wait(all) [a, b]")
        assert isinstance(ast.statements[0], WaitNode)
        assert ast.statements[0].mode == "all"

    def test_wait_any(self):
        ast = parse("wait(any) [a, b]")
        assert ast.statements[0].mode == "any"


class TestParserPrecedence:
    def test_multiplication_before_addition(self):
        ast = parse("1 + 2 * 3")
        assert isinstance(ast.statements[0], BinaryOpNode)
        assert ast.statements[0].op == "+"
        assert isinstance(ast.statements[0].right, BinaryOpNode)
        assert ast.statements[0].right.op == "*"

    def test_parentheses_override_precedence(self):
        ast = parse("(1 + 2) * 3")
        assert isinstance(ast.statements[0], BinaryOpNode)
        assert ast.statements[0].op == "*"
        assert isinstance(ast.statements[0].left, BinaryOpNode)
        assert ast.statements[0].left.op == "+"

    def test_and_before_or(self):
        ast = parse("a && b || c")
        assert ast.statements[0].op == "or"
        assert isinstance(ast.statements[0].left, BinaryOpNode)
        assert ast.statements[0].left.op == "and"


class TestParserComplex:
    def test_nested_function_calls(self):
        ast = parse("print(str(len(x)))")
        outer = ast.statements[0]
        assert isinstance(outer, FunctionCallNode)
        assert len(outer.args) == 1
        assert isinstance(outer.args[0], FunctionCallNode)

    def test_method_call_on_variable(self):
        ast = parse("list.append(1)")
        assert isinstance(ast.statements[0], CallNode)
        assert isinstance(ast.statements[0].callee, AttributeNode)

    def test_complex_expression(self):
        ast = parse("let result = (a + b) * (c - d) / e")
        assert isinstance(ast.statements[0], VarNode)
        assert isinstance(ast.statements[0].value, BinaryOpNode)

    def test_multiple_statements(self):
        ast = parse("let x = 1\nlet y = 2\nlet z = x + y")
        assert len(ast.statements) == 3
        assert all(isinstance(s, VarNode) for s in ast.statements)


class TestParserSyntaxErrors:
    def test_empty_program(self):
        lexer = Lexer("@")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        assert isinstance(ast, ProgramNode)
        assert len(ast.statements) == 0

    def test_unexpected_token_in_expression(self):
        lexer = Lexer("+ @")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with pytest.raises(SyntaxError):
            parser.parse()
