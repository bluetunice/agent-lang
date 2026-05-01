from dataclasses import dataclass


class AST:
    pass


@dataclass
class NumberNode(AST):
    value: float


@dataclass
class StringNode(AST):
    value: str


@dataclass
class BoolNode(AST):
    value: bool


@dataclass
class NullNode(AST):
    pass


@dataclass
class IdentifierNode(AST):
    name: str


@dataclass
class ListNode(AST):
    elements: list


@dataclass
class DictNode(AST):
    pairs: dict


@dataclass
class BinaryOpNode(AST):
    op: str
    left: AST
    right: AST


@dataclass
class UnaryOpNode(AST):
    op: str
    operand: AST


@dataclass
class TernaryNode(AST):
    condition: AST
    then_expr: AST
    else_expr: AST


@dataclass
class IfNode(AST):
    condition: AST
    then_branch: AST
    elseif_branches: list
    else_branch: AST


@dataclass
class ForNode(AST):
    variable: str
    iterable: AST
    body: AST


@dataclass
class WhileNode(AST):
    condition: AST
    body: AST


@dataclass
class FunctionDefNode(AST):
    name: str
    params: list
    body: AST
    return_type: str
    closure: dict = None


@dataclass
class FunctionCallNode(AST):
    name: AST
    args: list
    kwargs: dict


@dataclass
class CallNode(AST):
    callee: AST
    args: list


@dataclass
class ReturnNode(AST):
    value: AST


@dataclass
class BreakNode(AST):
    pass


@dataclass
class ContinueNode(AST):
    pass


@dataclass
class TryNode(AST):
    try_body: AST
    catch_body: AST
    finally_body: AST
    error_var: str = "error"


@dataclass
class ThrowNode(AST):
    value: AST


@dataclass
class ImportNode(AST):
    path: str
    alias: str


@dataclass
class FromImportNode(AST):
    path: str
    names: list


@dataclass
class ExportNode(AST):
    statement: AST


@dataclass
class TestNode(AST):
    name: str
    body: AST


@dataclass
class SuiteNode(AST):
    name: str
    tests: list


@dataclass
class ProgramNode(AST):
    statements: list


@dataclass
class BlockNode(AST):
    statements: list


@dataclass
class VarNode(AST):
    name: str
    value: AST
    type_name: str = None


@dataclass
class AttributeNode(AST):
    object: AST
    attribute: str


@dataclass
class IndexNode(AST):
    object: AST
    index: AST


@dataclass
class AssertNode(AST):
    condition: AST
    message: str = None


@dataclass
class AsyncNode(AST):
    body: AST


@dataclass
class AwaitNode(AST):
    expression: AST


@dataclass
class ParallelNode(AST):
    statements: list


@dataclass
class WaitNode(AST):
    mode: str
    expressions: list


@dataclass
class AssignNode(AST):
    target: AST     # IdentifierNode or IndexNode
    value: AST


@dataclass
class SetItemNode(AST):
    object: AST
    index: AST
    value: AST