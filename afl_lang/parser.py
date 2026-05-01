from afl_lang.lexer import Lexer, TokenType
from afl_lang.nodes import (
    ProgramNode, NumberNode, StringNode, BoolNode, NullNode, IdentifierNode,
    ListNode, DictNode, BinaryOpNode, UnaryOpNode, TernaryNode, IfNode, ForNode,
    WhileNode, FunctionDefNode, FunctionCallNode, CallNode, ReturnNode, BreakNode,
    ContinueNode, TryNode, ThrowNode, ImportNode, TestNode, SuiteNode, BlockNode,
    VarNode, AttributeNode, AssertNode, FromImportNode, ExportNode,
    AsyncNode, AwaitNode, ParallelNode, WaitNode, IndexNode,
    AssignNode, SetItemNode
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def expect(self, token_type):
        if self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type} at line {self.current_token.line}, col {self.current_token.col}, got {self.current_token.type}")
        token = self.current_token
        self.advance()
        return token

    def peek_next(self, offset=1):
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def is_at_end(self):
        return self.current_token.type == TokenType.EOF

    def parse(self):
        statements = []
        while not self.is_at_end():
            self.skip_newlines()
            if self.is_at_end():
                break
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements)

    def skip_newlines(self):
        while self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def statement(self):
        token_type = self.current_token.type
        if token_type == TokenType.LET:
            return self.var_declaration()
        elif token_type == TokenType.IF:
            return self.if_statement()
        elif token_type == TokenType.FOR:
            return self.for_statement()
        elif token_type == TokenType.WHILE:
            return self.while_statement()
        elif token_type == TokenType.FUNCTION:
            return self.function_definition()
        elif token_type == TokenType.RETURN:
            return self.return_statement()
        elif token_type == TokenType.BREAK:
            self.advance()
            return BreakNode()
        elif token_type == TokenType.CONTINUE:
            self.advance()
            return ContinueNode()
        elif token_type == TokenType.TRY:
            return self.try_statement()
        elif token_type == TokenType.THROW:
            return self.throw_statement()
        elif token_type == TokenType.ASSERT:
            return self.assert_statement()
        elif token_type == TokenType.TEST:
            if self.peek_next().type == TokenType.STRING:
                return self.test_statement()
            else:
                return self.expression_statement()
        elif token_type == TokenType.SUITE:
            return self.suite_statement()
        elif token_type == TokenType.IMPORT:
            return self.import_statement()
        elif token_type == TokenType.FROM:
            return self.from_import_statement()
        elif token_type == TokenType.EXPORT:
            return self.export_statement()
        elif token_type == TokenType.ASYNC:
            return self.async_statement()
        elif token_type == TokenType.AWAIT:
            return self.await_expression()
        elif token_type == TokenType.PARALLEL:
            return self.parallel_statement()
        elif token_type == TokenType.WAIT:
            return self.wait_statement()
        elif token_type == TokenType.IDENTIFIER:
            return self.expression_statement()
        else:
            return self.expression()

    def export_statement(self):
        self.expect(TokenType.EXPORT)
        if self.current_token.type == TokenType.FUNCTION:
            return self.function_definition()
        elif self.current_token.type == TokenType.LET:
            return self.var_declaration()
        else:
            self.advance()
            return None

    def var_declaration(self):
        self.expect(TokenType.LET)
        name = self.expect(TokenType.IDENTIFIER).value
        type_name = None
        if self.current_token.type == TokenType.COLON:
            self.advance()
            type_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.EQ)
        value = self.expression()
        return VarNode(name, value, type_name)

    def if_statement(self):
        self.expect(TokenType.IF)
        condition = self.expression()
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        then_branch = self.block()
        self.skip_newlines()
        self.expect(TokenType.RBRACE)
        elseif_branches = []
        else_branch = None
        self.skip_newlines()
        while self.current_token.type in (TokenType.ELSEIF, TokenType.ELSE):
            if self.current_token.type == TokenType.ELSEIF:
                self.advance()
            else:
                self.advance()
                self.skip_newlines()
                if self.current_token.type != TokenType.IF:
                    # Pure else branch — not "else if"
                    self.skip_newlines()
                    self.expect(TokenType.LBRACE)
                    self.skip_newlines()
                    else_branch = self.block()
                    self.skip_newlines()
                    self.expect(TokenType.RBRACE)
                    break
                self.advance()  # consume the 'if' token
            elseif_condition = self.expression()
            self.skip_newlines()
            self.expect(TokenType.LBRACE)
            self.skip_newlines()
            elseif_body = self.block()
            self.skip_newlines()
            self.expect(TokenType.RBRACE)
            elseif_branches.append((elseif_condition, elseif_body))
            self.skip_newlines()
        return IfNode(condition, then_branch, elseif_branches, else_branch)

    def for_statement(self):
        self.expect(TokenType.FOR)
        var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.expression()
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        body = self.block()
        self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return ForNode(var_name, iterable, body)

    def while_statement(self):
        self.expect(TokenType.WHILE)
        condition = self.expression()
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        body = self.block()
        self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return WhileNode(condition, body)

    def function_definition(self):
        self.expect(TokenType.FUNCTION)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        params = []
        while self.current_token.type != TokenType.RPAREN:
            param_name = self.expect(TokenType.IDENTIFIER).value
            param_type = None
            if self.current_token.type == TokenType.COLON:
                self.advance()
                param_type = self.expect(TokenType.IDENTIFIER).value
            default_val = None
            if self.current_token.type == TokenType.EQ:
                self.advance()
                default_val = self.expression()
            params.append((param_name, param_type, default_val))
            if self.current_token.type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RPAREN)
        return_type = None
        if self.current_token.type == TokenType.ARROW:
            self.advance()
            return_type = self.expect(TokenType.IDENTIFIER).value
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        body = self.block()
        self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return FunctionDefNode(name, params, body, return_type, closure=None)

    def return_statement(self):
        self.expect(TokenType.RETURN)
        value = NullNode()
        if not self.is_at_end() and self.current_token.type not in [TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF]:
            value = self.expression()
        return ReturnNode(value)

    def try_statement(self):
        self.expect(TokenType.TRY)
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        try_body = self.block()
        self.skip_newlines()
        self.expect(TokenType.RBRACE)
        self.skip_newlines()
        catch_body = None
        error_var = "error"
        if self.current_token.type == TokenType.CATCH:
            self.advance()
            self.skip_newlines()
            if self.current_token.type == TokenType.IDENTIFIER:
                error_var = self.current_token.value
                self.advance()
            self.skip_newlines()
            self.expect(TokenType.LBRACE)
            self.skip_newlines()
            catch_body = self.block()
            self.skip_newlines()
            self.expect(TokenType.RBRACE)
            self.skip_newlines()
        finally_body = None
        if self.current_token.type == TokenType.FINALLY:
            self.advance()
            self.skip_newlines()
            self.expect(TokenType.LBRACE)
            self.skip_newlines()
            finally_body = self.block()
            self.skip_newlines()
            self.expect(TokenType.RBRACE)
        return TryNode(try_body, catch_body, finally_body, error_var)

    def throw_statement(self):
        self.expect(TokenType.THROW)
        value = self.expression()
        return ThrowNode(value)

    def assert_statement(self):
        self.expect(TokenType.ASSERT)
        condition = self.expression()
        message = None
        if self.current_token.type == TokenType.COMMA:
            self.advance()
            if self.current_token.type == TokenType.STRING:
                message = self.current_token.value
                self.advance()
        return AssertNode(condition, message)

    def test_statement(self):
        self.expect(TokenType.TEST)
        name = self.expect(TokenType.STRING).value
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        body = self.block()
        self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return TestNode(name, body)

    def suite_statement(self):
        self.expect(TokenType.SUITE)
        name = self.expect(TokenType.STRING).value
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        tests = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.TEST:
                tests.append(self.test_statement())
            self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return SuiteNode(name, tests)

    def import_statement(self):
        self.expect(TokenType.IMPORT)
        path = self.expect(TokenType.STRING).value
        alias = None
        if self.current_token.type == TokenType.AS:
            self.advance()
            alias = self.expect(TokenType.IDENTIFIER).value
        return ImportNode(path, alias)

    def from_import_statement(self):
        self.expect(TokenType.FROM)
        path = self.expect(TokenType.STRING).value
        self.expect(TokenType.IMPORT)
        names = []
        name = self.expect(TokenType.IDENTIFIER).value
        names.append(name)
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            names.append(name)
        return FromImportNode(path, names)

    def block(self):
        statements = []
        while self.current_token.type not in [TokenType.RBRACE, TokenType.EOF]:
            self.skip_newlines()
            if self.current_token.type in [TokenType.RBRACE, TokenType.EOF]:
                break
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return BlockNode(statements)

    def expression_statement(self):
        return self.expression()

    def expression(self):
        left = self.logical_or()
        # Handle ?? (nullish coalescing)
        if self.current_token.type == TokenType.QQ:
            self.advance()
            right = self.logical_or()
            left = BinaryOpNode("??", left, right)
        if self.current_token.type == TokenType.EQ:
            self.advance()
            right = self.expression()
            if isinstance(left, IdentifierNode):
                return AssignNode(left, right)
            elif isinstance(left, IndexNode):
                return SetItemNode(left.object, left.index, right)
            elif isinstance(left, AttributeNode):
                return AssignNode(left, right)
            raise SyntaxError(f"Invalid assignment target at line {self.current_token.line}")
        return left

    def logical_or(self):
        left = self.logical_and()
        while self.current_token.type == TokenType.OR:
            self.advance()
            right = self.logical_and()
            left = BinaryOpNode("or", left, right)
        return left

    def logical_and(self):
        left = self.comparison()
        while self.current_token.type == TokenType.AND:
            self.advance()
            right = self.comparison()
            left = BinaryOpNode("and", left, right)
        return left

    def comparison(self):
        left = self.addition()
        while self.current_token.type in [TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE, TokenType.EQEQ, TokenType.NEQ]:
            op = self.current_token.value
            self.advance()
            right = self.addition()
            left = BinaryOpNode(op, left, right)
        # Handle 'in' operator (membership test)
        if self.current_token.type == TokenType.IN:
            self.advance()
            right = self.addition()
            left = BinaryOpNode("in", left, right)
        return self.ternary(left)

    def ternary(self, condition):
        if self.current_token.type in [TokenType.THEN, TokenType.IF]:
            self.advance()
            then_expr = self.logical_or()
            self.skip_newlines()
            if self.current_token.type == TokenType.ELSE:
                self.advance()
                else_expr = self.logical_or()
                return TernaryNode(condition, then_expr, else_expr)
            else:
                raise SyntaxError(f"Expected 'else' at line {self.current_token.line}")
        return condition

    def addition(self):
        left = self.multiplication()
        while self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token.value
            self.advance()
            right = self.multiplication()
            left = BinaryOpNode(op, left, right)
        return left

    def multiplication(self):
        left = self.unary()
        while self.current_token.type in [TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.STARSTAR]:
            op = self.current_token.value
            self.advance()
            right = self.unary()
            left = BinaryOpNode(op, left, right)
        return left

    def unary(self):
        if self.current_token.type in [TokenType.MINUS, TokenType.NOT]:
            op = self.current_token.value
            self.advance()
            operand = self.unary()
            return UnaryOpNode(op, operand)
        return self.postfix()

    def postfix(self):
        node = self.primary()
        while self.current_token.type in (TokenType.DOT, TokenType.LBRACKET):
            if self.current_token.type == TokenType.DOT:
                self.advance()
                if self.current_token.type == TokenType.IDENTIFIER:
                    prop = self.current_token.value
                    self.advance()
                    if self.current_token.type == TokenType.LPAREN:
                        args = self.arguments()
                        node = CallNode(AttributeNode(node, prop), args)
                    else:
                        node = AttributeNode(node, prop)
            elif self.current_token.type == TokenType.LBRACKET:
                self.advance()
                index = self.expression()
                self.expect(TokenType.RBRACKET)
                node = IndexNode(node, index)
        return node

    def primary(self):
        token = self.current_token
        token_type = token.type

        if token_type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.value)
        elif token_type == TokenType.STRING:
            self.advance()
            return StringNode(token.value)
        elif token_type == TokenType.BOOL:
            self.advance()
            return BoolNode(token.value)
        elif token_type == TokenType.NULL:
            self.advance()
            return NullNode()
        elif token_type == TokenType.IF:
            return self.inline_if()
        elif token_type == TokenType.IDENTIFIER:
            self.advance()
            if self.current_token.type == TokenType.LPAREN:
                return self.function_call(IdentifierNode(token.value))
            return IdentifierNode(token.value)
        elif token_type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.expect(TokenType.RPAREN)
            return expr
        elif token_type == TokenType.LBRACKET:
            self.advance()
            elements = []
            while self.current_token.type != TokenType.RBRACKET:
                elements.append(self.expression())
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
                elif self.current_token.type != TokenType.RBRACKET:
                    break
            self.expect(TokenType.RBRACKET)
            return ListNode(elements)
        elif token_type == TokenType.LBRACE:
            self.advance()
            pairs = {}
            while self.current_token.type != TokenType.RBRACE:
                if self.current_token.type in [TokenType.STRING, TokenType.IDENTIFIER]:
                    key = self.current_token.value
                    self.advance()
                    self.expect(TokenType.COLON)
                    value = self.expression()
                    pairs[key] = value
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
                elif self.current_token.type != TokenType.RBRACE:
                    break
            self.expect(TokenType.RBRACE)
            return DictNode(pairs)
        elif token_type == TokenType.QUESTION:
            self.advance()
            condition = self.expression()
            self.expect(TokenType.QUESTION)
            then_expr = self.expression()
            self.expect(TokenType.COLON)
            else_expr = self.expression()
            return TernaryNode(condition, then_expr, else_expr)
        else:
                raise SyntaxError(f"Unexpected token: {token_type} at line {token.line}, col {token.col}")

    def arguments(self):
        self.expect(TokenType.LPAREN)
        args = []
        kwargs = {}
        
        if self.current_token.type != TokenType.RPAREN:
            while True:
                if self.current_token.type == TokenType.IDENTIFIER and self.peek_next().type == TokenType.EQ:
                    key = self.current_token.value
                    self.advance()
                    self.advance()
                    value = self.expression()
                    kwargs[key] = value
                else:
                    args.append(self.expression())
                
                if self.current_token.type != TokenType.COMMA:
                    break
                self.advance()
        
        self.expect(TokenType.RPAREN)
        return args, kwargs

    def function_call(self, name):
        args, kwargs = self.arguments()
        return FunctionCallNode(name, args, kwargs)

    def inline_if(self):
        self.advance()
        condition = self.logical_or()
        if self.current_token.type == TokenType.THEN:
            self.advance()
            then_expr = self.logical_or()
            if self.current_token.type == TokenType.ELSE:
                self.advance()
                else_expr = self.logical_or()
                return TernaryNode(condition, then_expr, else_expr)
        return condition

    def async_statement(self):
        self.expect(TokenType.ASYNC)
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        body = self.block()
        self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return AsyncNode(body)

    def await_expression(self):
        self.expect(TokenType.AWAIT)
        expr = self.expression()
        return AwaitNode(expr)

    def parallel_statement(self):
        self.expect(TokenType.PARALLEL)
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        statements = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type in [TokenType.RBRACE, TokenType.EOF]:
                break
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return ParallelNode(statements)

    def wait_statement(self):
        self.expect(TokenType.WAIT)
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            mode = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.RPAREN)
        else:
            mode = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACKET)
        expressions = []
        while self.current_token.type != TokenType.RBRACKET:
            expressions.append(self.expression())
            if self.current_token.type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RBRACKET)
        return WaitNode(mode, expressions)