import json
import time
import os
import uuid
import base64
import hashlib
import re
import subprocess
import sys

from afl_lang.lexer import Lexer
from afl_lang.parser import Parser
from afl_lang.nodes import (
    ProgramNode, NumberNode, StringNode, BoolNode, NullNode, IdentifierNode,
    ListNode, DictNode, BinaryOpNode, UnaryOpNode, TernaryNode, IfNode, ForNode,
    WhileNode, FunctionDefNode, FunctionCallNode, CallNode, ReturnNode, BreakNode,
    ContinueNode, TryNode, ThrowNode, ImportNode, TestNode, SuiteNode, BlockNode,
    VarNode, AttributeNode, IndexNode, AssertNode, FromImportNode, ExportNode,
    AsyncNode, AwaitNode, ParallelNode, WaitNode,
    AssignNode, SetItemNode
)


class AFLObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class SkillModule(AFLObject):
    """内置 skill 模块 - 支持动态 skill 导入和调用.

    skill.load("name")       # 导入 skill
    skill.run("name", opts)  # 运行 skill
    skill.list()             # 列出已导入 skills
    skill.<name>.<method>()  # 直接调用 skill 方法
    """

    def __init__(self, interpreter):
        self._interp = interpreter
        self._registry = {}

    def load(self, name, opts=None):
        return self._interp._skill_import(name, opts, self._registry)

    def import_skill(self, name, opts=None):
        """别名, 与 load() 相同. 注意: 在 AFL 中 .import 是关键字, 请用 .load()."""
        return self._interp._skill_import(name, opts, self._registry)

    def run(self, name, opts=None):
        return self._interp._skill_run(name, opts, self._registry)

    def list(self):
        return list(self._registry.keys())

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        reg = self._registry
        if name in reg:
            return reg[name]
        try:
            self._interp._skill_import(name, None, reg)
        except Exception:
            pass
        if name in reg:
            return reg[name]
        raise AttributeError(
            f"Skill '{name}' not found. "
            f"Use skill.import('{name}') first, or check skill.list() for available skills."
        )

    def __getitem__(self, key):
        reg = self._registry
        if key in reg:
            return reg[key]
        try:
            self._interp._skill_import(key, None, reg)
        except Exception:
            pass
        if key in reg:
            return reg[key]
        raise KeyError(f"Skill '{key}' not found")


class Interpreter:
    TYPE_MAP = {
        "string": str,
        "number": (int, float),
        "bool": bool,
        "list": list,
        "dict": dict,
        "function": FunctionDefNode,
    }
    
    BUILTIN_FUNCTIONS = {
        "print": ("_builtin_print", None),
        "range": ("_builtin_range", None),
        "len": ("_builtin_len", None),
        "type": ("_builtin_type", None),
        "int": ("_builtin_int", None),
        "float": ("_builtin_float", None),
        "str": ("_builtin_str", None),
        "bool": ("_builtin_bool", None),
        "json": ("_builtin_json", None),
        "assert_eq": ("_builtin_assert_eq", None),
        "abs": ("_builtin_abs", None),
        "max": ("_builtin_max", None),
        "min": ("_builtin_min", None),
        "round": ("_builtin_round", None),
        "append": ("_builtin_append", None),
        "pop": ("_builtin_pop", None),
        "time": ("_builtin_time", None),
        "regex": ("_builtin_regex", None),
        "env": ("_builtin_env", None),
        "path": ("_builtin_path", None),
        "uuid": ("_builtin_uuid", None),
        "base64": ("_builtin_base64", None),
        "hash": ("_builtin_hash", None),
        "rand": ("_builtin_rand", None),
        "sort": ("_builtin_sort", None),
        "filter": ("_builtin_filter", None),
        "map": ("_builtin_map", None),
        "reduce": ("_builtin_reduce", None),
    }

    BUILTIN_MODULES = {
        "log": "_builtin_log",
        "api": "_builtin_api",
        "llm": "_builtin_llm",
        "kb": "_builtin_kb",
        "mcp": "_builtin_mcp",
        "skill": "_builtin_skill",
        "input": "_builtin_input",
        "output": "_builtin_output",
        "cmd": "_builtin_cmd",
        "test": "_builtin_test",
    }

    SKILL_PRESETS = {
        "math": {
            "add": lambda a, b=0: a + b,
            "subtract": lambda a, b=0: a - b,
            "multiply": lambda a, b=1: a * b,
            "divide": lambda a, b=1: a / b if b != 0 else None,
            "abs": lambda a: abs(a),
            "floor": lambda a: int(a),
            "ceil": lambda a: int(a) + 1 if a != int(a) else int(a),
            "round": lambda a, n=0: round(a, n),
            "sum": lambda *args: sum(args),
            "avg": lambda *args: sum(args) / len(args) if args else 0,
            "sqrt": lambda a: a ** 0.5,
            "pow": lambda a, b: a ** b,
            "min": lambda *args: min(args),
            "max": lambda *args: max(args),
            "clamp": lambda v, lo, hi: max(lo, min(hi, v)),
        },
        "text": {
            "upper": lambda s: str(s).upper(),
            "lower": lambda s: str(s).lower(),
            "trim": lambda s: str(s).strip(),
            "replace": lambda s, old, new: str(s).replace(old, new),
            "split": lambda s, sep=" ": str(s).split(sep),
            "join": lambda items, sep=", ": sep.join(str(i) for i in items),
            "contains": lambda s, sub: sub in str(s),
            "starts_with": lambda s, prefix: str(s).startswith(prefix),
            "ends_with": lambda s, suffix: str(s).endswith(suffix),
            "length": lambda s: len(str(s)),
            "substring": lambda s, start=0, end=None: str(s)[start:end],
            "reverse": lambda s: str(s)[::-1],
            "format": lambda t, **kw: str(t).format(**kw) if kw else str(t),
            "pad_left": lambda s, w, c=" ": str(s).rjust(w, c),
            "pad_right": lambda s, w, c=" ": str(s).ljust(w, c),
            "count": lambda s, sub: str(s).count(sub),
            "find": lambda s, sub: str(s).find(sub),
            "capitalize": lambda s: str(s).capitalize(),
        },
        "data": {
            "get": lambda d, key, default=None: d.get(key, default) if isinstance(d, dict) else default,
            "keys": lambda d: list(d.keys()) if isinstance(d, dict) else [],
            "values": lambda d: list(d.values()) if isinstance(d, dict) else [],
            "items": lambda d: list(d.items()) if isinstance(d, dict) else [],
            "flatten": lambda lst: [item for sublist in lst for item in sublist] if lst else [],
            "unique": lambda lst: list(dict.fromkeys(lst)) if lst else [],
            "sort": lambda lst, reverse=False: sorted(lst, reverse=reverse),
            "reverse": lambda lst: list(reversed(lst)) if lst else [],
            "first": lambda lst: lst[0] if lst else None,
            "last": lambda lst: lst[-1] if lst else None,
            "take": lambda lst, n: lst[:n],
            "drop": lambda lst, n: lst[n:],
            "slice": lambda lst, start=0, end=None: lst[start:end],
            "chunk": lambda lst, n: [lst[i:i+n] for i in range(0, len(lst), n)] if lst else [],
            "merge": lambda *dicts: {k: v for d in dicts if isinstance(d, dict) for k, v in d.items()},
            "pick": lambda d, *keys: {k: d[k] for k in keys if k in d} if isinstance(d, dict) else {},
            "omit": lambda d, *keys: {k: v for k, v in d.items() if k not in keys} if isinstance(d, dict) else {},
        },
    }

    OPERATORS = {
        "+": lambda l, r: str(l) + str(r) if isinstance(l, str) or isinstance(r, str) else l + r,
        "-": lambda l, r: l - r,
        "*": lambda l, r: l * r,
        "/": lambda l, r: l / r,
        "%": lambda l, r: l % r,
        "**": lambda l, r: l ** r,
        "==": lambda l, r: l == r,
        "!=": lambda l, r: l != r,
        "<": lambda l, r: l < r,
        "<=": lambda l, r: l <= r,
        ">": lambda l, r: l > r,
        ">=": lambda l, r: l >= r,
        "and": lambda l, r: bool(l and r),
        "or": lambda l, r: bool(l or r),
        "??": lambda l, r: l if l is not None else r,
        "in": lambda l, r: l in r if hasattr(r, "__contains__") else False,
    }

    def __init__(self):
        self.scopes = [{}]
        self.functions = {}
        self.modules = {}
        self.exports = set()
        self.tests = {}
        self.suites = {}
        self.break_flag = False
        self.continue_flag = False
        self.return_value = None

    def _push_scope(self):
        self.scopes.append({})

    def _pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def _get_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        if name in self.modules:
            return self.modules[name]
        for module in self.modules.values():
            if hasattr(module, name):
                return getattr(module, name)
        if name in self.functions:
            return self.functions[name]
        if name in self.BUILTIN_MODULES:
            return getattr(self, self.BUILTIN_MODULES[name])([], {})
        return None

    def _set_var(self, name, value, type_name=None):
        if type_name and type_name in self.TYPE_MAP:
            expected = self.TYPE_MAP[type_name]
            if not isinstance(value, expected):
                raise TypeError(f"Expected {type_name}, got {type(value).__name__}")
        self.scopes[-1][name] = value

    def interpret(self, node):
        if isinstance(node, ProgramNode):
            return self.run_program(node)
        return None

    def run_program(self, node):
        result = None
        for stmt in node.statements:
            if isinstance(stmt, FunctionDefNode):
                stmt.closure = dict(self.scopes[-1])
                self.functions[stmt.name] = stmt
            elif isinstance(stmt, TestNode):
                self.tests[stmt.name] = stmt
            elif isinstance(stmt, SuiteNode):
                self.suites[stmt.name] = stmt
            else:
                result = self.eval(stmt)
        return result

    def eval(self, node):
        if node is None:
            return None
        elif isinstance(node, BlockNode):
            return self.eval_block(node)
        elif isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BoolNode):
            return node.value
        elif isinstance(node, NullNode):
            return None
        elif isinstance(node, IdentifierNode):
            return self._get_var(node.name)
        elif isinstance(node, ListNode):
            return [self.eval(e) for e in node.elements]
        elif isinstance(node, DictNode):
            return {k: self.eval(v) for k, v in node.pairs.items()}
        elif isinstance(node, IndexNode):
            obj = self.eval(node.object)
            idx = self.eval(node.index)
            if isinstance(obj, (list, tuple, str)):
                return obj[int(idx)]
            elif isinstance(obj, dict):
                return obj.get(idx) if isinstance(idx, str) else obj.get(str(idx))
            try:
                return obj[idx]
            except (TypeError, KeyError, IndexError, AttributeError):
                return None
        elif isinstance(node, BinaryOpNode):
            return self.eval_binary(node)
        elif isinstance(node, UnaryOpNode):
            return self.eval_unary(node)
        elif isinstance(node, TernaryNode):
            cond = self.eval(node.condition)
            return self.eval(node.then_expr if cond else node.else_expr)
        elif isinstance(node, VarNode):
            value = self.eval(node.value)
            self._set_var(node.name, value, node.type_name)
            return value
        elif isinstance(node, IfNode):
            return self.eval_if(node)
        elif isinstance(node, ForNode):
            return self.eval_for(node)
        elif isinstance(node, WhileNode):
            return self.eval_while(node)
        elif isinstance(node, BreakNode):
            self.break_flag = True
            return None
        elif isinstance(node, ContinueNode):
            self.continue_flag = True
            return None
        elif isinstance(node, ThrowNode):
            msg = self.eval(node.value)
            raise Exception(msg)
        elif isinstance(node, ReturnNode):
            self.return_value = self.eval(node.value)
            return self.return_value
        elif isinstance(node, FunctionDefNode):
            node.closure = dict(self.scopes[-1])
            self.functions[node.name] = node
            return node
        elif isinstance(node, AssertNode):
            return self.eval_assert(node)
        elif isinstance(node, TryNode):
            return self.eval_try(node)
        elif isinstance(node, ImportNode):
            return self.eval_import(node)
        elif isinstance(node, FromImportNode):
            return self.eval_from_import(node)
        elif isinstance(node, ExportNode):
            return self.eval_export(node)
        elif isinstance(node, TestNode):
            self.tests[node.name] = node
            return None
        elif isinstance(node, SuiteNode):
            self.suites[node.name] = node
            return None
        elif isinstance(node, AsyncNode):
            return self.eval_async(node)
        elif isinstance(node, AwaitNode):
            return self.eval_await(node)
        elif isinstance(node, ParallelNode):
            return self.eval_parallel(node)
        elif isinstance(node, WaitNode):
            return self.eval_wait(node)
        elif isinstance(node, FunctionCallNode):
            return self.eval_function_call(node)
        elif isinstance(node, CallNode):
            return self.eval_call(node)
        elif isinstance(node, AttributeNode):
            return self.eval_attribute(node)
        elif isinstance(node, AssignNode):
            return self.eval_assign(node)
        elif isinstance(node, SetItemNode):
            return self.eval_setitem(node)
        return None

    def eval_binary(self, node):
        left = self.eval(node.left)
        right = self.eval(node.right)
        op = node.op
        if op in self.OPERATORS:
            return self.OPERATORS[op](left, right)
        return None

    def eval_unary(self, node):
        operand = self.eval(node.operand)
        if node.op == "-":
            return -operand
        elif node.op == "not":
            return not operand
        return operand

    def eval_if(self, node):
        if self.eval(node.condition):
            return self.eval(node.then_branch)
        for cond, branch in node.elseif_branches:
            if self.eval(cond):
                return self.eval(branch)
        if node.else_branch:
            return self.eval(node.else_branch)
        return None

    def eval_for(self, node):
        iterable = self.eval(node.iterable)
        if isinstance(iterable, str):
            iterable = list(iterable)
        for item in iterable:
            self._set_var(node.variable, item)
            self.eval(node.body)
            if self.break_flag:
                self.break_flag = False
                break
            if self.continue_flag:
                self.continue_flag = False
        return None

    def eval_while(self, node):
        while self.eval(node.condition):
            self.eval(node.body)
            if self.break_flag:
                self.break_flag = False
                break
            if self.continue_flag:
                self.continue_flag = False
        return None

    def eval_block(self, node):
        result = None
        for stmt in node.statements:
            result = self.eval(stmt)
            if self.return_value is not None:
                break
            if self.break_flag or self.continue_flag:
                break
        return result

    def eval_attribute(self, node):
        obj = self.eval(node.object)
        if obj is None:
            return None
        return getattr(obj, node.attribute, None)

    def eval_call(self, node):
        callee = self.eval(node.callee)
        if isinstance(node.args, tuple) and len(node.args) == 2:
            pos_args, kwargs = node.args
            args = [self.eval(a) for a in pos_args]
            kwargs = {k: self.eval(v) for k, v in kwargs.items()}
        else:
            args = [self.eval(a) for a in node.args]
            kwargs = {}
        if callee and hasattr(callee, 'call'):
            return callee.call(*args, **kwargs)
        if callee and hasattr(callee, '__call__'):
            return callee(*args, **kwargs)
        return None

    def eval_assert(self, node):
        result = self.eval(node.condition)
        if not result:
            msg = node.message if node.message else "Assertion failed"
            raise AssertionError(msg)
        return True

    def eval_try(self, node):
        try:
            self.eval(node.try_body)
        except Exception as e:
            error_msg = str(e)
            error_var = node.error_var if hasattr(node, 'error_var') else "error"
            self._set_var(error_var, error_msg)
            if node.catch_body:
                self.eval(node.catch_body)
            self.scopes[-1].pop(error_var, None)
        finally:
            if node.finally_body:
                self.eval(node.finally_body)
        return None

    def eval_import(self, node):
        path = node.path
        import_as = node.alias if node.alias else None
        try:
            with open(path, "r") as f:
                code = f.read()
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            module_vars = {}
            module_funcs = {}
            for stmt in ast.statements:
                if isinstance(stmt, FunctionDefNode):
                    module_funcs[stmt.name] = stmt
                elif isinstance(stmt, VarNode):
                    val = self.eval(stmt.value)
                    module_vars[stmt.name] = val
                elif isinstance(stmt, TestNode):
                    self.tests[stmt.name] = stmt
                elif isinstance(stmt, SuiteNode):
                    self.suites[stmt.name] = stmt
            if import_as:
                self.modules[import_as] = AFLObject(**module_vars, **module_funcs)
            else:
                self.functions.update(module_funcs)
                self.scopes[-1].update(module_vars)
            return None
        except Exception as e:
            print(f"Import error: {e}")
            return None

    def eval_from_import(self, node):
        path = node.path
        try:
            with open(path, "r") as f:
                code = f.read()
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            module_vars = {}
            module_funcs = {}
            for stmt in ast.statements:
                if isinstance(stmt, FunctionDefNode):
                    module_funcs[stmt.name] = stmt
                elif isinstance(stmt, VarNode):
                    val = self.eval(stmt.value)
                    module_vars[stmt.name] = val
            for name in node.names:
                if name in module_funcs:
                    self.functions[name] = module_funcs[name]
                elif name in module_vars:
                    self.scopes[-1][name] = module_vars[name]
                else:
                    print(f"Import error: {name} not found in {path}")
            return None
        except Exception as e:
            print(f"Import error: {e}")
            return None

    def eval_async(self, node):
        import asyncio
        async def run_async():
            self._push_scope()
            result = self.eval(node.body)
            self._pop_scope()
            return result
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(run_async())
        except RuntimeError:
            return asyncio.run(run_async())

    def eval_await(self, node):
        import asyncio
        expr = self.eval(node.expression)
        if asyncio.iscoroutine(expr):
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(expr)
            except RuntimeError:
                return asyncio.run(expr)
        return expr

    def eval_parallel(self, node):
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.eval, stmt) for stmt in node.statements]
            concurrent.futures.wait(futures)
            return [f.result() for f in futures]

    def eval_wait(self, node):
        results = [self.eval(expr) for expr in node.expressions]
        if node.mode == "all":
            return results
        elif node.mode == "any":
            return results[0] if results else None
        return results

    def eval_assign(self, node):
        value = self.eval(node.value)
        if isinstance(node.target, IdentifierNode):
            name = node.target.name
            for scope in reversed(self.scopes):
                if name in scope:
                    scope[name] = value
                    return value
            self._set_var(name, value)
            return value
        elif isinstance(node.target, AttributeNode):
            obj = self.eval(node.target.object)
            if obj:
                setattr(obj, node.target.attribute, value)
            return value
        return None

    def eval_setitem(self, node):
        value = self.eval(node.value)
        obj = self.eval(node.object)
        idx = self.eval(node.index)
        if isinstance(obj, dict):
            obj[idx] = value
        elif isinstance(obj, (list, tuple)) and isinstance(idx, int):
            obj[idx] = value
        elif isinstance(obj, list):
            obj[int(idx)] = value
        return value

    def eval_function_call(self, node):
        if isinstance(node.name, IdentifierNode):
            name = node.name.name
            if name in self.functions:
                func = self.functions[name]
                return self.call_function(func, node.args, node.kwargs)
            func = self._get_var(name)
            if isinstance(func, FunctionDefNode):
                return self.call_function(func, node.args, node.kwargs)
            if name in self.BUILTIN_FUNCTIONS:
                method_name, _ = self.BUILTIN_FUNCTIONS[name]
                return getattr(self, method_name)(node.args, node.kwargs)
        else:
            callee = self.eval(node.name)
            if isinstance(callee, FunctionDefNode):
                return self.call_function(callee, node.args, node.kwargs)
        return None

    def call_function(self, func, args, kwargs):
        if isinstance(func, FunctionDefNode):
            self._push_scope()
            if func.closure:
                self.scopes[-1].update(func.closure)
            for i, (param, _, default_val) in enumerate(func.params):
                if i < len(args):
                    self._set_var(param, self.eval(args[i]))
                elif isinstance(kwargs, dict) and param in kwargs:
                    self._set_var(param, self.eval(kwargs[param]))
                elif default_val is not None:
                    self._set_var(param, self.eval(default_val))
            self.return_value = None
            result = self.eval(func.body)
            self._pop_scope()
            return result or self.return_value
        return None

    def _builtin_assert_eq(self, args, kwargs):
        if len(args) >= 2:
            actual = self.eval(args[0])
            expected = self.eval(args[1])
            if actual != expected:
                raise AssertionError(f"assert_eq failed: expected {expected}, got {actual}")
            return True
        return False

    def _builtin_test(self, args, kwargs):
        return AFLObject(run=lambda *args: self._run_tests(args[0] if args else None))

    def _run_tests(self, suite_name=None):
        passed = 0
        failed = 0
        
        if suite_name and suite_name in self.suites:
            suite = self.suites[suite_name]
            for test_node in suite.tests:
                try:
                    self.eval(test_node.body)
                    passed += 1
                    print(f"PASS: {test_node.name}")
                except Exception as e:
                    failed += 1
                    print(f"FAIL: {test_node.name} - {e}")
        else:
            for test_name, test_node in self.tests.items():
                try:
                    self.eval(test_node.body)
                    passed += 1
                    print(f"PASS: {test_name}")
                except Exception as e:
                    failed += 1
                    print(f"FAIL: {test_name} - {e}")
            for suite_name, suite in self.suites.items():
                for test_node in suite.tests:
                    try:
                        self.eval(test_node.body)
                        passed += 1
                        print(f"PASS: {suite_name}/{test_node.name}")
                    except Exception as e:
                        failed += 1
                        print(f"FAIL: {suite_name}/{test_node.name} - {e}")
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0

    def _builtin_print(self, args, kwargs):
        output = " ".join(str(self.eval(a)) for a in args)
        print(output)
        return None

    def _builtin_range(self, args, kwargs):
        if not args:
            return []
        start = 0
        stop = 0
        step = 1
        if len(args) == 1:
            stop = int(self.eval(args[0]))
        elif len(args) == 2:
            start = int(self.eval(args[0]))
            stop = int(self.eval(args[1]))
        elif len(args) == 3:
            start = int(self.eval(args[0]))
            stop = int(self.eval(args[1]))
            step = int(self.eval(args[2]))
        return list(range(start, stop, step))

    def _builtin_len(self, args, kwargs):
        val = self.eval(args[0]) if args else []
        return len(val) if val else 0

    def _builtin_type(self, args, kwargs):
        val = self.eval(args[0]) if args else None
        if val is None:
            return "NoneType"
        return type(val).__name__

    def _builtin_int(self, args, kwargs):
        val = self.eval(args[0]) if args else 0
        return int(val) if val is not None else 0

    def _builtin_float(self, args, kwargs):
        val = self.eval(args[0]) if args else 0.0
        return float(val) if val is not None else 0.0

    def _builtin_str(self, args, kwargs):
        val = self.eval(args[0]) if args else ""
        return str(val) if val is not None else ""

    def _builtin_bool(self, args, kwargs):
        val = self.eval(args[0]) if args else False
        return bool(val) if val is not None else False

    def _builtin_abs(self, args, kwargs):
        val = self.eval(args[0]) if args else 0
        return abs(val) if val is not None else 0

    def _builtin_max(self, args, kwargs):
        vals = [self.eval(a) for a in args] if args else []
        return max(vals) if vals else None

    def _builtin_min(self, args, kwargs):
        vals = [self.eval(a) for a in args] if args else []
        return min(vals) if vals else None

    def _builtin_round(self, args, kwargs):
        val = self.eval(args[0]) if args else 0
        return round(val) if val is not None else 0

    def _builtin_append(self, args, kwargs):
        if len(args) >= 2:
            lst = self.eval(args[0])
            val = self.eval(args[1])
            if isinstance(lst, list):
                lst.append(val)
        return None

    def _builtin_pop(self, args, kwargs):
        if args:
            lst = self.eval(args[0])
            if isinstance(lst, list):
                return lst.pop() if lst else None
        return None

    def _builtin_rand(self, args, kwargs):
        import random
        if len(args) == 1:
            return random.randint(0, int(self.eval(args[0])) - 1)
        elif len(args) >= 2:
            return random.randint(int(self.eval(args[0])), int(self.eval(args[1])))
        return random.random()

    def _builtin_sort(self, args, kwargs):
        if args:
            lst = self.eval(args[0])
            if isinstance(lst, list):
                return sorted(lst)
        return []

    def _builtin_filter(self, args, kwargs):
        if len(args) >= 2:
            func = self.eval(args[0])
            lst = self.eval(args[1])
            if isinstance(lst, list):
                def call_func(func, *args):
                    if isinstance(func, FunctionDefNode):
                        return self.call_function(func, [NumberNode(a) if isinstance(a, (int, float)) else a for a in args], {})
                    elif callable(func):
                        return func(*args)
                    return None
                return [x for x in lst if call_func(func, x)]
        return []

    def _builtin_map(self, args, kwargs):
        if len(args) >= 2:
            func = self.eval(args[0])
            lst = self.eval(args[1])
            if isinstance(lst, list):
                def call_func(func, *args):
                    if isinstance(func, FunctionDefNode):
                        return self.call_function(func, [NumberNode(a) if isinstance(a, (int, float)) else a for a in args], {})
                    elif callable(func):
                        return func(*args)
                    return None
                return [call_func(func, x) for x in lst]
        return []

    def _builtin_reduce(self, args, kwargs):
        if len(args) >= 2:
            func = self.eval(args[0])
            lst = self.eval(args[1])
            if isinstance(lst, list) and lst:
                def call_func(func, *args):
                    if isinstance(func, FunctionDefNode):
                        return self.call_function(func, [NumberNode(a) if isinstance(a, (int, float)) else a for a in args], {})
                    elif callable(func):
                        return func(*args)
                    return None
                result = lst[0]
                for x in lst[1:]:
                    result = call_func(func, result, x)
                return result
        return None

    def _builtin_json(self, args, kwargs):
        if not args:
            return AFLObject(parse=lambda x: json.loads(x), stringify=lambda x: json.dumps(x))
        val = self.eval(args[0])
        if isinstance(val, dict):
            return json.dumps(val)
        if isinstance(val, str):
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return None
        return None

    def _builtin_time(self, args, kwargs):
        return time.time()

    def _builtin_regex(self, args, kwargs):
        if not args:
            return AFLObject(match=lambda p, t: re.search(p, t), replace=lambda p, r, t: re.sub(p, r, t))
        raw_args = [self.eval(a) for a in args]
        if len(raw_args) >= 2:
            op = str(raw_args[0])
            if op == "match" and len(raw_args) >= 2:
                return re.search(str(raw_args[1]), str(raw_args[2])) if len(raw_args) > 2 else None
            elif op == "replace" and len(raw_args) >= 3:
                return re.sub(str(raw_args[1]), str(raw_args[3]), str(raw_args[2]))
            else:
                m = re.search(str(raw_args[0]), str(raw_args[1]))
                return m.group(0) if m else None
        return None

    def _builtin_env(self, args, kwargs):
        if not args:
            return AFLObject(get=lambda k: os.environ.get(k), set=lambda k, v: setattr(os.environ, k, v))
        raw_args = [self.eval(a) for a in args]
        if len(raw_args) == 1:
            return os.environ.get(str(raw_args[0]))
        elif len(raw_args) >= 2:
            op = str(raw_args[0])
            if op == "get" and len(raw_args) > 1:
                return os.environ.get(str(raw_args[1]))
            elif op == "set" and len(raw_args) > 2:
                os.environ[str(raw_args[1])] = str(raw_args[2])
        return None

    def _builtin_path(self, args, kwargs):
        if not args:
            return AFLObject(join=lambda *p: os.path.join(*p), dirname=lambda p: os.path.dirname(p), basename=lambda p: os.path.basename(p))
        raw_args = [self.eval(a) for a in args]
        op = str(raw_args[0])
        parts = raw_args[1:]
        if op == "join":
            return os.path.join(*[str(p) for p in parts])
        elif op == "dirname" and parts:
            return os.path.dirname(str(parts[0]))
        elif op == "basename" and parts:
            return os.path.basename(str(parts[0]))
        return None

    def _builtin_uuid(self, args, kwargs):
        return str(uuid.uuid4())

    def _builtin_base64(self, args, kwargs):
        if not args:
            return AFLObject(encode=lambda x: base64.b64encode(x.encode()).decode(), decode=lambda x: base64.b64decode(x.encode()).decode())
        raw_args = [self.eval(a) for a in args]
        op = str(raw_args[0])
        data = str(raw_args[1]) if len(raw_args) > 1 else ""
        if op == "encode":
            return base64.b64encode(data.encode()).decode()
        elif op == "decode":
            try:
                return base64.b64decode(data).decode()
            except Exception:
                return base64.b64decode(data.encode()).decode()
        return None

    def _builtin_hash(self, args, kwargs):
        if not args:
            return AFLObject(sha256=lambda x: hashlib.sha256(x.encode()).hexdigest())
        raw_args = [self.eval(a) for a in args]
        op = str(raw_args[0])
        data = str(raw_args[1]) if len(raw_args) > 1 else ""
        if op == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif op == "md5":
            return hashlib.md5(data.encode()).hexdigest()
        return hashlib.sha256(data.encode()).hexdigest()

    def _builtin_input(self, args, kwargs):
        if not args:
            return AFLObject(
                args=lambda: sys.argv[1:],
                stdin=lambda: sys.stdin.read() if not sys.stdin.isatty() else input(),
                prompt=lambda p: sys.argv[1] if len(sys.argv) > 1 else input(p),
                env=lambda k: os.environ.get(k) if k else None,
            )
        if args:
            first = self.eval(args[0])
            op = str(first) if not isinstance(first, str) else first
            if op == "args":
                return sys.argv[1:] if len(sys.argv) > 1 else []
            elif op == "stdin":
                return sys.stdin.read() if not sys.stdin.isatty() else input()
            elif op == "prompt" and len(args) > 1:
                prompt_text = str(self.eval(args[1]))
                return sys.argv[1] if len(sys.argv) > 1 else input(prompt_text)
            elif op == "env" and len(args) > 1:
                return os.environ.get(str(self.eval(args[1])), "")
        return None

    def _builtin_output(self, args, kwargs):
        if not args:
            return AFLObject(file=lambda p, c: self._write_file(p, c))
        if args:
            first = args[0]
            if hasattr(first, 'name'):
                op = first.name
            else:
                op = str(first)
            if op == "file" and len(args) > 2:
                path = str(self.eval(args[1]))
                content = str(self.eval(args[2]))
                self._write_file(path, content)
        return None

    def _write_file(self, path, content):
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)

    def _make_api_module(self):
        interp = self
        return AFLObject(
            call=lambda *a, **kw: interp._api_call(a[0], a[1], a[2] if len(a) > 2 else kw),
            get=lambda *a, **kw: interp._api_call("GET", a[0], a[1] if len(a) > 1 else kw),
            post=lambda *a, **kw: interp._api_call("POST", a[0], a[1] if len(a) > 1 else kw),
            put=lambda *a, **kw: interp._api_call("PUT", a[0], a[1] if len(a) > 1 else kw),
            delete=lambda *a, **kw: interp._api_call("DELETE", a[0], a[1] if len(a) > 1 else kw),
        )

    def _api_call(self, method, url, opts=None):
        import urllib.request, urllib.parse, json as _json
        opts = opts or {}
        headers = {"User-Agent": "AFL/1.0"}
        body = None
        timeout = 30
        params = {}

        method = str(opts.get("method", method)).upper()
        if "url" in opts:
            url = str(opts["url"])
        if "headers" in opts and isinstance(opts["headers"], dict):
            headers.update(opts["headers"])
        if "timeout" in opts:
            timeout = float(opts["timeout"])
        if "params" in opts and isinstance(opts["params"], dict):
            params = opts["params"]
        if "body" in opts:
            body = opts["body"]
            if isinstance(body, dict):
                body = _json.dumps(body).encode()
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
            elif isinstance(body, str):
                body = body.encode()

        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)

        if body and method == "GET":
            method = "POST"

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            resp = urllib.request.urlopen(req, timeout=timeout)
            resp_body = resp.read()
            body_str = resp_body.decode() if resp_body else ""
            result = AFLObject(
                status=resp.status,
                headers=dict(resp.headers),
                body=body_str,
                json=lambda b=body_str: _json.loads(b) if b else {},
                text=body_str,
                ok=200 <= resp.status < 300,
            )
            return result
        except urllib.error.HTTPError as e:
            err_body = e.read().decode() if e.fp else str(e)
            return AFLObject(
                status=e.code,
                headers=dict(e.headers),
                body=err_body,
                json=lambda: {},
                text=err_body,
                ok=False,
            )
        except Exception as e:
            return AFLObject(
                status=0, headers={}, body=str(e), json=lambda: {},
                text=str(e), ok=False,
            )

    def _builtin_api(self, args, kwargs):
        return self._make_api_module()

    def _builtin_mcp(self, args, kwargs):
        if not args:
            return AFLObject(connect=lambda url: None, list_tools=lambda: [], call_tool=lambda n, a: {})
        if args:
            first = args[0]
            if hasattr(first, 'name'):
                op = first.name
            else:
                op = str(first)
            if op == "connect":
                url = str(self.eval(args[1])) if len(args) > 1 else ""
                print(f"[mcp.connect] {url}")
            elif op == "list_tools":
                return []
            elif op == "call_tool":
                print(f"[mcp.call_tool]")
                return {}
        return None

    # ── Skill 模块 ──────────────────────────────────────────────

    def _builtin_skill(self, args, kwargs):
        if not hasattr(self, '_skill_cache'):
            self._skill_cache = SkillModule(self)
        return self._skill_cache

    def _skill_import(self, name, opts, registry):
        """导入 skill: 支持内置预设、本地 .agent/.afl 文件。"""
        # 1) 内置预设 skill
        preset = self.SKILL_PRESETS.get(name)
        if preset:
            mod = AFLObject(**preset)
            registry[name] = mod
            return mod

        # 2) 文件形式: <name>.agent / <name>.afl / skills/<name>.*
        search_paths = []
        for ext in ('.agent', '.afl'):
            if name.endswith(ext):
                search_paths.append(name)
            else:
                search_paths.append(f"{name}{ext}")
                search_paths.append(f"skills/{name}{ext}")

        for path in search_paths:
            if os.path.isfile(path):
                return self._load_skill_file(path, name, registry)

        raise ValueError(
            f"Skill '{name}' not found. "
            f"Available presets: {', '.join(self.SKILL_PRESETS)}"
        )

    def _skill_run(self, name, opts, registry):
        """运行已导入的 skill，opts 可以指定 action/method 和参数。"""
        if name not in registry:
            self._skill_import(name, None, registry)
        mod = registry.get(name)
        if mod is None:
            raise ValueError(f"Skill '{name}' not found")

        # opts = { action: "method", ...params } 或 { method: "method", ...params }
        if isinstance(opts, dict):
            action = opts.pop("action", None) or opts.pop("method", None)
            if action:
                fn = getattr(mod, action, None)
                if fn is None:
                    raise AttributeError(f"Skill '{name}' has no method '{action}'")
                return fn(**opts) if opts else fn()
            # 如果 opts 只有一个 key，视为参数直接传递给默认方法
            return mod(**opts) if hasattr(mod, '__call__') else mod
        return mod

    def _skill_list(self, registry):
        return list(registry.keys())

    def _load_skill_file(self, path, name, registry):
        """从 .agent/.afl 文件加载 skill。"""
        with open(path, 'r') as f:
            code = f.read()
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        exports = {}
        for stmt in ast.statements:
            # Parser 的 export_statement 直接返回内部节点（不包裹 ExportNode）
            if isinstance(stmt, FunctionDefNode):
                exports[stmt.name] = self._make_skill_func(stmt)
            elif isinstance(stmt, VarNode):
                exports[stmt.name] = self.eval(stmt.value)
        mod = AFLObject(**exports)
        registry[name] = mod
        return mod

    def _make_skill_func(self, func_node):
        """将 FunctionDefNode 包装为可调用的 Python 函数。"""
        interp = self

        def wrapper(*args, **kwargs):
            interp._push_scope()
            if func_node.closure:
                interp.scopes[-1].update(func_node.closure)
            for i, (param, _, default_val) in enumerate(func_node.params):
                if i < len(args):
                    interp._set_var(param, args[i])
                elif param in kwargs:
                    interp._set_var(param, kwargs[param])
                elif default_val is not None:
                    interp._set_var(param, interp.eval(default_val))
            interp.return_value = None
            result = interp.eval(func_node.body)
            interp._pop_scope()
            return result if result is not None else interp.return_value
        return wrapper

    def _builtin_llm(self, args, kwargs):
        if not args:
            return AFLObject(
                new=lambda o, **kw: AFLObject(provider=o.get("provider") if isinstance(o, dict) else o, model=o.get("model") if isinstance(o, dict) else ""),
                chat=lambda m: AFLObject(content="LLM response"),
                prompt=lambda t, v=None: "LLM response"
            )
        if args:
            first = args[0]
            if hasattr(first, 'name'):
                op = first.name
            else:
                op = str(first)
            if op == "new":
                return AFLObject(provider="openai", model="gpt-4")
            elif op == "chat":
                print("[llm.chat]")
                return AFLObject(content="LLM response")
            elif op == "prompt":
                return "LLM response"
        return None

    def _builtin_kb(self, args, kwargs):
        if not args:
            return AFLObject(connect=lambda n, o: None, search=lambda q, **kwargs: [])
        if args:
            first = args[0]
            if hasattr(first, 'name'):
                op = first.name
            else:
                op = str(first)
            if op == "connect":
                print(f"[kb.connect]")
            elif op == "search":
                print(f"[kb.search]")
                return []
        return None

    def _builtin_log(self, args, kwargs):
        if not args:
            log_obj = AFLObject(
                info=lambda msg: print(f"[INFO] {msg}"),
                debug=lambda msg: print(f"[DEBUG] {msg}"),
                warn=lambda msg: print(f"[WARN] {msg}"),
                error=lambda msg: print(f"[ERROR] {msg}")
            )
            return log_obj
        return None

    def _builtin_cmd(self, args, kwargs):
        cmd_mod = self._make_cmd_module()
        if not args:
            return cmd_mod
        if args:
            first = args[0]
            op = first.name if hasattr(first, 'name') else str(first)
            if op == "run" and len(args) > 1:
                cmd = str(self.eval(args[1]))
                timeout = float(self.eval(args[2])) if len(args) > 2 else 30
                return self._cmd_exec(cmd, timeout)
            elif op == "pipe" and len(args) > 1:
                return self._cmd_exec(str(self.eval(args[1])), 30)
            elif op == "which" and len(args) > 1:
                return self._cmd_which(str(self.eval(args[1])))
            elif op == "exists" and len(args) > 1:
                return self._cmd_exists(str(self.eval(args[1])))
            elif op == "type" and len(args) > 1:
                return self._cmd_type(str(self.eval(args[1])))
            elif op == "help" and len(args) > 1:
                return self._cmd_help(str(self.eval(args[1])))
            elif op == "version" and len(args) > 1:
                return self._cmd_version(str(self.eval(args[1])))
            elif op == "man" and len(args) > 1:
                return self._cmd_man(str(self.eval(args[1])))
        return None

    def _make_cmd_module(self):
        import platform as _platform
        import getpass as _getpass
        import tempfile as _tempfile
        interp = self

        return AFLObject(
            run=lambda c, t=30: interp._cmd_exec(c, t),
            pipe=lambda c: interp._cmd_exec(c, 30),
            which=lambda n: interp._cmd_which(n),
            exists=lambda n: interp._cmd_exists(n),
            type=lambda n: interp._cmd_type(n),
            help=lambda n: interp._cmd_help(n),
            version=lambda n: interp._cmd_version(n),
            man=lambda n: interp._cmd_man(n),
            getenv=lambda k: os.environ.get(k),
            env=dict(os.environ),
            path=os.environ.get("PATH", "").split(":") if os.environ.get("PATH") else [],
            cwd=os.getcwd(),
            home=os.path.expanduser("~"),
            tmpdir=_tempfile.gettempdir(),
            platform=AFLObject(
                system=_platform.system(),
                release=_platform.release(),
                version=_platform.version(),
                machine=_platform.machine(),
                processor=_platform.processor() or "",
                python=_platform.python_version(),
            ),
            shell=AFLObject(
                user=_getpass.getuser(),
                path=os.environ.get("SHELL", ""),
                home=os.path.expanduser("~"),
                hostname=os.uname().nodename,
            ),
        )

    def _cmd_exec(self, command, timeout=30, cwd=None, env=None):
        timeout = min(float(timeout), 300) if timeout else 30
        import time as _time
        start = _time.time()
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=cwd, env=env,
            )
            duration = round(_time.time() - start, 3)
            return AFLObject(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                success=result.returncode == 0,
                duration=duration,
            )
        except subprocess.TimeoutExpired:
            return AFLObject(
                stdout="", stderr=f"Command timed out after {timeout}s",
                exit_code=124, success=False, duration=float(timeout),
            )
        except Exception as e:
            return AFLObject(
                stdout="", stderr=str(e),
                exit_code=-1, success=False, duration=0,
            )

    def _cmd_which(self, name):
        result = self._cmd_exec(f"which {name}", 5)
        path = result.stdout.strip()
        return AFLObject(found=bool(path), path=path if path else None)

    def _cmd_exists(self, name):
        result = self._cmd_exec(f"command -v {name} 2>&1", 5)
        return bool(result.stdout.strip()) and result.exit_code == 0

    def _cmd_type(self, name):
        result = self._cmd_exec(f"type {name} 2>&1", 5)
        stdout = result.stdout.strip()
        if "builtin" in stdout or "is a shell builtin" in stdout:
            return "builtin"
        if "aliased" in stdout or "is an alias" in stdout:
            return "alias"
        if name in stdout and ("is" in stdout or "/" in stdout):
            return "file"
        return "unknown"

    def _cmd_help(self, name):
        result = self._cmd_exec(f"{name} --help 2>&1 || {name} -h 2>&1", 10)
        return result.stdout if result.stdout else result.stderr

    def _cmd_version(self, name):
        for flag in ["--version", "version", "-V", "-version"]:
            result = self._cmd_exec(f"{name} {flag} 2>&1", 5)
            if result.stdout.strip() and result.exit_code == 0:
                return result.stdout.strip()
        return ""

    def _cmd_man(self, name):
        result = self._cmd_exec(f"man {name} 2>&1 | col -b 2>/dev/null | head -60", 10)
        return result.stdout if result.stdout else f"No man page found for {name}"


def repl():
    print("AgentFlow Language REPL v1.4")
    print("Type 'exit' to quit, 'help' for help")
    interpreter = Interpreter()
    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break
        if line.strip() == "exit":
            break
        if line.strip() == "help":
            print("AFL REPL - type expressions or statements")
            continue
        if not line.strip():
            continue
        try:
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            result = interpreter.interpret(ast)
            if result is not None:
                print(repr(result))
        except Exception as e:
            print(f"Error: {e}")


def run_agent(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    return interpreter.interpret(ast)


def run_file(path: str):
    with open(path, "r") as f:
        return run_agent(f.read())


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            run_agent(f.read())
    else:
        print("AgentFlow Language v1.1")
        print("Usage: python3 afl_lang/agent.py <file.agent>")


if __name__ == "__main__":
    main()