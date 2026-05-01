import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from afl_lang.nodes import (
    AST, NumberNode, StringNode, BoolNode, NullNode, IdentifierNode,
    ListNode, DictNode, BinaryOpNode, UnaryOpNode, TernaryNode, IfNode, ForNode,
    WhileNode, FunctionDefNode, FunctionCallNode, CallNode, ReturnNode, BreakNode,
    ContinueNode, TryNode, ThrowNode, ImportNode, TestNode, SuiteNode, BlockNode,
    VarNode, AttributeNode, AssertNode, FromImportNode, ExportNode,
    AsyncNode, AwaitNode, ParallelNode, WaitNode, IndexNode,
    AssignNode, SetItemNode, ProgramNode
)


class TestASTBase:
    def test_ast_is_class(self):
        assert issubclass(AST, object)

    def test_nodes_inherit_from_ast(self):
        for node_class in [
            NumberNode, StringNode, BoolNode, NullNode, IdentifierNode,
            ListNode, DictNode, BinaryOpNode, UnaryOpNode, TernaryNode, IfNode,
            ForNode, WhileNode, FunctionDefNode, FunctionCallNode, CallNode,
            ReturnNode, BreakNode, ContinueNode, TryNode, ThrowNode,
            ImportNode, TestNode, SuiteNode, BlockNode, VarNode, AttributeNode,
            AssertNode, FromImportNode, ExportNode, AsyncNode, AwaitNode,
            ParallelNode, WaitNode, IndexNode, AssignNode, SetItemNode
        ]:
            assert issubclass(node_class, AST)


class TestLiteralNodes:
    def test_number_node(self):
        n = NumberNode(42)
        assert n.value == 42

    def test_number_node_float(self):
        n = NumberNode(3.14)
        assert n.value == 3.14

    def test_string_node(self):
        n = StringNode("hello")
        assert n.value == "hello"

    def test_bool_node_true(self):
        n = BoolNode(True)
        assert n.value is True

    def test_bool_node_false(self):
        n = BoolNode(False)
        assert n.value is False

    def test_null_node(self):
        n = NullNode()
        assert n is not None


class TestIdentifierNode:
    def test_identifier(self):
        n = IdentifierNode("myVar")
        assert n.name == "myVar"


class TestContainerNodes:
    def test_list_node_empty(self):
        n = ListNode([])
        assert len(n.elements) == 0

    def test_list_node_with_elements(self):
        n = ListNode([NumberNode(1), NumberNode(2)])
        assert len(n.elements) == 2

    def test_dict_node_empty(self):
        n = DictNode({})
        assert len(n.pairs) == 0

    def test_dict_node_with_pairs(self):
        n = DictNode({"key": StringNode("value")})
        assert "key" in n.pairs


class TestExpressionNodes:
    def test_binary_op(self):
        n = BinaryOpNode("+", NumberNode(1), NumberNode(2))
        assert n.op == "+"
        assert isinstance(n.left, NumberNode)
        assert isinstance(n.right, NumberNode)

    def test_unary_op(self):
        n = UnaryOpNode("-", NumberNode(5))
        assert n.op == "-"
        assert isinstance(n.operand, NumberNode)

    def test_ternary(self):
        n = TernaryNode(BoolNode(True), NumberNode(1), NumberNode(2))
        assert isinstance(n.condition, BoolNode)
        assert isinstance(n.then_expr, NumberNode)
        assert isinstance(n.else_expr, NumberNode)


class TestControlFlowNodes:
    def test_if_node(self):
        n = IfNode(
            BoolNode(True),
            BlockNode([]),
            [],
            None
        )
        assert isinstance(n.condition, BoolNode)
        assert isinstance(n.then_branch, BlockNode)
        assert len(n.elseif_branches) == 0
        assert n.else_branch is None

    def test_for_node(self):
        n = ForNode("i", NumberNode(10), BlockNode([]))
        assert n.variable == "i"
        assert isinstance(n.body, BlockNode)

    def test_while_node(self):
        n = WhileNode(BoolNode(True), BlockNode([]))
        assert isinstance(n.condition, BoolNode)
        assert isinstance(n.body, BlockNode)

    def test_break_node(self):
        n = BreakNode()
        assert n is not None

    def test_continue_node(self):
        n = ContinueNode()
        assert n is not None


class TestFunctionNodes:
    def test_function_def(self):
        n = FunctionDefNode("add", [("a", None, None), ("b", None, None)], BlockNode([]), None)
        assert n.name == "add"
        assert len(n.params) == 2
        assert n.return_type is None
        assert n.closure is None

    def test_function_def_with_defaults(self):
        params = [("name", "string", StringNode("world"))]
        n = FunctionDefNode("greet", params, BlockNode([]), "string")
        assert n.params[0][2] is not None
        assert n.return_type == "string"

    def test_function_call(self):
        n = FunctionCallNode(IdentifierNode("print"), [StringNode("hi")], {})
        assert isinstance(n.name, IdentifierNode)
        assert len(n.args) == 1

    def test_function_call_with_kwargs(self):
        n = FunctionCallNode(IdentifierNode("foo"), [], {"a": NumberNode(1)})
        assert "a" in n.kwargs

    def test_call_node(self):
        n = CallNode(AttributeNode(IdentifierNode("obj"), "method"), [NumberNode(1)])
        assert isinstance(n.callee, AttributeNode)
        assert len(n.args) == 1

    def test_return_node(self):
        n = ReturnNode(NumberNode(42))
        assert isinstance(n.value, NumberNode)


class TestErrorHandlingNodes:
    def test_try_node(self):
        n = TryNode(BlockNode([]), BlockNode([]), None, "e")
        assert isinstance(n.try_body, BlockNode)
        assert isinstance(n.catch_body, BlockNode)
        assert n.finally_body is None
        assert n.error_var == "e"

    def test_try_node_default_error_var(self):
        n = TryNode(BlockNode([]), None, None)
        assert n.error_var == "error"

    def test_throw_node(self):
        n = ThrowNode(StringNode("error"))
        assert isinstance(n.value, StringNode)


class TestModuleNodes:
    def test_import_node(self):
        n = ImportNode("module.agent", None)
        assert n.path == "module.agent"
        assert n.alias is None

    def test_import_node_with_alias(self):
        n = ImportNode("module.agent", "mod")
        assert n.alias == "mod"

    def test_from_import_node(self):
        n = FromImportNode("module.agent", ["foo", "bar"])
        assert n.path == "module.agent"
        assert n.names == ["foo", "bar"]

    def test_export_node(self):
        n = ExportNode(VarNode("x", NumberNode(1)))
        assert isinstance(n.statement, VarNode)


class TestTestNodes:
    def test_test_node(self):
        n = TestNode("my test", BlockNode([]))
        assert n.name == "my test"
        assert isinstance(n.body, BlockNode)

    def test_suite_node(self):
        n = SuiteNode("my suite", [TestNode("t1", BlockNode([]))])
        assert n.name == "my suite"
        assert len(n.tests) == 1


class TestStructureNodes:
    def test_program_node(self):
        n = ProgramNode([NumberNode(1), NumberNode(2)])
        assert len(n.statements) == 2

    def test_block_node(self):
        n = BlockNode([NumberNode(1), StringNode("hi")])
        assert len(n.statements) == 2

    def test_var_node(self):
        n = VarNode("x", NumberNode(10), None)
        assert n.name == "x"
        assert n.type_name is None

    def test_var_node_with_type(self):
        n = VarNode("x", NumberNode(10), "number")
        assert n.type_name == "number"


class TestAccessNodes:
    def test_attribute_node(self):
        n = AttributeNode(IdentifierNode("obj"), "method")
        assert isinstance(n.object, IdentifierNode)
        assert n.attribute == "method"

    def test_index_node(self):
        n = IndexNode(IdentifierNode("arr"), NumberNode(0))
        assert isinstance(n.object, IdentifierNode)
        assert isinstance(n.index, NumberNode)


class TestAssertNode:
    def test_assert_without_message(self):
        n = AssertNode(BoolNode(True))
        assert n.message is None

    def test_assert_with_message(self):
        n = AssertNode(BoolNode(True), "should be true")
        assert n.message == "should be true"


class TestAsyncNodes:
    def test_async_node(self):
        n = AsyncNode(BlockNode([]))
        assert isinstance(n.body, BlockNode)

    def test_await_node(self):
        n = AwaitNode(FunctionCallNode(IdentifierNode("foo"), [], {}))
        assert isinstance(n.expression, FunctionCallNode)

    def test_parallel_node(self):
        n = ParallelNode([NumberNode(1), NumberNode(2)])
        assert len(n.statements) == 2

    def test_wait_node(self):
        n = WaitNode("all", [IdentifierNode("a"), IdentifierNode("b")])
        assert n.mode == "all"
        assert len(n.expressions) == 2


class TestAssignmentNodes:
    def test_assign_node(self):
        n = AssignNode(IdentifierNode("x"), NumberNode(10))
        assert isinstance(n.target, IdentifierNode)
        assert isinstance(n.value, NumberNode)

    def test_setitem_node(self):
        n = SetItemNode(IdentifierNode("arr"), NumberNode(0), NumberNode(10))
        assert isinstance(n.object, IdentifierNode)
        assert isinstance(n.index, NumberNode)
        assert isinstance(n.value, NumberNode)
