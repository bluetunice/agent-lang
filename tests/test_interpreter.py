import pytest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from afl_lang import run_agent, run_file, Interpreter, AFLObject, SkillModule
from afl_lang.lexer import Lexer
from afl_lang.parser import Parser
from afl_lang.nodes import (
    ProgramNode, NumberNode, StringNode, BoolNode, NullNode, IdentifierNode,
    ListNode, DictNode, BinaryOpNode, UnaryOpNode, IfNode, ForNode,
    WhileNode, FunctionDefNode, FunctionCallNode, ReturnNode, BreakNode,
    ContinueNode, TryNode, ThrowNode, TestNode, SuiteNode, BlockNode,
    VarNode, AssertNode, AsyncNode, AwaitNode, ParallelNode, WaitNode,
    AssignNode, SetItemNode, IndexNode, AttributeNode, CallNode,
)


class TestInterpreterLiterals:
    def test_number(self):
        assert run_agent("42") == 42

    def test_string(self):
        assert run_agent('"hello"') == "hello"

    def test_true(self):
        assert run_agent("true") is True

    def test_false(self):
        assert run_agent("false") is False

    def test_null(self):
        assert run_agent("null") is None

    def test_float(self):
        assert run_agent("3.14") == 3.14


class TestInterpreterVariables:
    def test_var_declaration(self):
        result = run_agent("let x = 10\nx")
        assert result == 10

    def test_string_variable(self):
        result = run_agent('let name = "world"\nname')
        assert result == "world"

    def test_var_reassignment(self):
        result = run_agent("let x = 10\nx = 20\nx")
        assert result == 20

    def test_var_with_expression(self):
        result = run_agent("let x = 1 + 2\nx")
        assert result == 3

    def test_typed_variable(self):
        result = run_agent("let x: number = 42\nx")
        assert result == 42

    def test_typed_variable_type_error(self):
        with pytest.raises(TypeError):
            run_agent("let x: string = 42")


class TestInterpreterOperators:
    def test_addition(self):
        assert run_agent("1 + 2") == 3

    def test_subtraction(self):
        assert run_agent("10 - 3") == 7

    def test_multiplication(self):
        assert run_agent("4 * 5") == 20

    def test_division(self):
        assert run_agent("10 / 2") == 5.0

    def test_modulo(self):
        assert run_agent("10 % 3") == 1

    def test_power(self):
        assert run_agent("2 ** 3") == 8

    def test_equality_true(self):
        assert run_agent("1 == 1") is True

    def test_equality_false(self):
        assert run_agent("1 == 2") is False

    def test_not_equal(self):
        assert run_agent("1 != 2") is True

    def test_less_than(self):
        assert run_agent("1 < 2") is True

    def test_less_equal(self):
        assert run_agent("2 <= 2") is True

    def test_greater_than(self):
        assert run_agent("2 > 1") is True

    def test_greater_equal(self):
        assert run_agent("2 >= 2") is True

    def test_and(self):
        assert run_agent("true && true") is True

    def test_and_false(self):
        assert run_agent("true && false") is False

    def test_or(self):
        assert run_agent("false || true") is True

    def test_or_false(self):
        assert run_agent("false || false") is False

    def test_nullish_coalescing_with_value(self):
        assert run_agent("let x = 10\nx ?? 0") == 10

    def test_nullish_coalescing_with_null(self):
        assert run_agent("let x = null\nx ?? 42") == 42

    def test_in_operator_list(self):
        assert run_agent("let lst = [1, 2, 3]\n2 in lst") is True

    def test_in_operator_string(self):
        assert run_agent('"ell" in "hello"') is True

    def test_unary_minus(self):
        assert run_agent("let x = 5\n-x") == -5

    def test_not_operator(self):
        assert run_agent("not true") is False

    def test_not_false(self):
        assert run_agent("not false") is True

    def test_string_concatenation(self):
        assert run_agent('"hello" + " " + "world"') == "hello world"

    def test_string_repeat(self):
        assert run_agent('"ab" * 3') == "ababab"


class TestInterpreterConditionals:
    def test_if_true(self):
        result = run_agent("if true { 42 }")
        assert result == 42

    def test_if_false(self):
        result = run_agent("if false { 42 }")
        assert result is None

    def test_if_else_true(self):
        result = run_agent("if true { 1 } else { 2 }")
        assert result == 1

    def test_if_else_false(self):
        result = run_agent("if false { 1 } else { 2 }")
        assert result == 2

    def test_elseif(self):
        result = run_agent("let x = 2\nif x == 1 { 1 } elseif x == 2 { 2 } else { 3 }")
        assert result == 2

    def test_elseif_fallthrough(self):
        result = run_agent("let x = 3\nif x == 1 { 1 } elseif x == 2 { 2 } else { 3 }")
        assert result == 3


class TestInterpreterLoops:
    def test_for_range(self):
        result = run_agent("let sum = 0\nfor i in range(5) { sum = sum + i }\nsum")
        assert result == 10

    def test_for_list(self):
        result = run_agent("let sum = 0\nfor x in [1, 2, 3] { sum = sum + x }\nsum")
        assert result == 6

    def test_for_string(self):
        result = run_agent("let s = ''\nfor c in 'ab' { s = s + c }\ns")
        assert result == "ab"

    def test_while_loop(self):
        result = run_agent("let i = 0\nwhile i < 3 { i = i + 1 }\ni")
        assert result == 3

    def test_break(self):
        result = run_agent("let sum = 0\nfor i in range(10) { if i == 3 { break } sum = sum + i }\nsum")
        assert result == 3

    def test_continue(self):
        result = run_agent("let sum = 0\nfor i in range(5) { if i == 2 { continue } sum = sum + i }\nsum")
        assert result == 8

    def test_while_break(self):
        result = run_agent("let i = 0\nwhile i < 10 { i = i + 1\nif i == 5 { break } }\ni")
        assert result == 5

    def test_while_continue(self):
        result = run_agent("let i = 0\nlet count = 0\nwhile i < 5 { i = i + 1\nif i == 3 { continue }\ncount = count + 1 }\ncount")
        assert result == 4


class TestInterpreterFunctions:
    def test_function_call(self):
        result = run_agent("function add(a, b) { return a + b }\nadd(3, 4)")
        assert result == 7

    def test_function_default_param(self):
        result = run_agent("function greet(name = 'world') { return name }\ngreet()")
        assert result == "world"

    def test_function_keyword_arg(self):
        result = run_agent("function add(a, b) { return a + b }\nadd(a = 1, b = 2)")
        assert result == 3

    def test_function_return_value(self):
        result = run_agent("function foo() { return 42 }\nfoo()")
        assert result == 42

    def test_function_no_return(self):
        result = run_agent("function foo() { let x = 1 }\nfoo()")
        assert result is None or result == 1

    def test_recursive_function(self):
        result = run_agent(
            "function fib(n) { if n <= 1 { return n } return fib(n-1) + fib(n-2) }\nfib(10)"
        )
        assert result == 55

    def test_function_closure(self):
        result = run_agent(
            "let x = 10\nfunction get_x() { return x }\nget_x()"
        )
        assert result == 10


class TestInterpreterLists:
    def test_list_literal(self):
        result = run_agent("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_list_index(self):
        result = run_agent("[1, 2, 3][0]")
        assert result == 1

    def test_list_index_negative(self):
        result = run_agent("[1, 2, 3][-1]")
        assert result == 3

    def test_list_length(self):
        result = run_agent("len([1, 2, 3])")
        assert result == 3

    def test_append(self):
        result = run_agent("let lst = [1, 2]\nappend(lst, 3)\nlst")
        assert result == [1, 2, 3]

    def test_pop(self):
        result = run_agent("let lst = [1, 2, 3]\npop(lst)")
        assert result == 3

    def test_setitem_list(self):
        result = run_agent("let lst = [1, 2, 3]\nlst[0] = 10\nlst[0]")
        assert result == 10


class TestInterpreterDicts:
    def test_dict_literal(self):
        result = run_agent('{"a": 1, "b": 2}')
        assert result == {"a": 1, "b": 2}

    def test_dict_access(self):
        result = run_agent('let d = {"a": 1}\nd["a"]')
        assert result == 1

    def test_dict_setitem(self):
        result = run_agent('let d = {"a": 1}\nd["b"] = 2\nd["b"]')
        assert result == 2

    def test_dict_get_nonexistent(self):
        result = run_agent('let d = {"a": 1}\nd["b"]')
        assert result is None


class TestInterpreterTernary:
    def test_question_ternary(self):
        result = run_agent("? true then 1 else 2")
        assert result == 1


class TestInterpreterErrorHandling:
    def test_try_catch(self):
        result = run_agent("let msg = ''\ntry { throw 'error' } catch e { msg = e }\nmsg")
        assert result == "error"

    def test_try_finally(self):
        result = run_agent("let done = false\ntry { let x = 1 } finally { done = true }\ndone")
        assert result is True

    def test_try_catch_finally(self):
        result = run_agent(
            "let msg = ''\nlet done = false\n"
            "try { throw 'fail' } catch e { msg = e } finally { done = true }\n"
            "msg + ':' + str(done)"
        )
        assert result == "fail:True"

    def test_try_no_error(self):
        result = run_agent("let x = 0\ntry { x = 1 } catch e { x = 2 }\nx")
        assert result == 1

    def test_assert_true(self):
        result = run_agent("assert true")
        assert result is True

    def test_assert_false(self):
        with pytest.raises(AssertionError):
            run_agent("assert false")

    def test_assert_with_message(self):
        with pytest.raises(AssertionError, match="custom message"):
            run_agent('assert false, "custom message"')

    def test_throw(self):
        with pytest.raises(Exception, match="my error"):
            run_agent("throw 'my error'")


class TestInterpreterBuiltinFunctions:
    def test_builtin_print(self, capsys):
        run_agent('print("hello")')
        captured = capsys.readouterr()
        assert "hello" in captured.out

    def test_builtin_range(self):
        assert run_agent("range(5)") == [0, 1, 2, 3, 4]

    def test_builtin_range_start_stop(self):
        assert run_agent("range(2, 5)") == [2, 3, 4]

    def test_builtin_range_step(self):
        assert run_agent("range(0, 10, 2)") == [0, 2, 4, 6, 8]

    def test_builtin_len_string(self):
        assert run_agent('len("hello")') == 5

    def test_builtin_len_list(self):
        assert run_agent("len([1, 2, 3])") == 3

    def test_builtin_type(self):
        assert run_agent("type(42)") == "int"

    def test_builtin_type_string(self):
        assert run_agent('type("hello")') == "str"

    def test_builtin_type_list(self):
        assert run_agent("type([1, 2])") == "list"

    def test_builtin_type_none(self):
        assert run_agent("type(null)") == "NoneType"

    def test_builtin_int(self):
        assert run_agent('int("42")') == 42

    def test_builtin_int_default(self):
        assert run_agent("int(null)") == 0

    def test_builtin_float(self):
        assert run_agent('float("3.14")') == 3.14

    def test_builtin_str(self):
        assert run_agent("str(42)") == "42"

    def test_builtin_bool(self):
        assert run_agent("bool(1)") is True
        assert run_agent("bool(0)") is False

    def test_builtin_abs(self):
        assert run_agent("abs(-5)") == 5

    def test_builtin_max(self):
        assert run_agent("max(1, 5, 3)") == 5

    def test_builtin_min(self):
        assert run_agent("min(1, 5, 3)") == 1

    def test_builtin_round(self):
        assert run_agent("round(3.7)") == 4

    def test_builtin_json_stringify(self):
        result = run_agent('let d = {"a": 1}\njson(d)')
        assert json.loads(result) == {"a": 1}

    def test_builtin_json_parse(self):
        result = run_agent('json(\'{"a": 1}\')')
        assert result == {"a": 1}

    def test_builtin_json_module(self):
        result = run_agent("let j = json()\nj.parse('{\"x\": 1}')")
        assert result == {"x": 1}

    def test_builtin_uuid(self):
        result = run_agent("uuid()")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_builtin_time(self):
        result = run_agent("time()")
        assert isinstance(result, float)
        assert result > 0

    def test_builtin_sort(self):
        result = run_agent("sort([3, 1, 2])")
        assert result == [1, 2, 3]

    def test_builtin_rand(self):
        result = run_agent("rand(10)")
        assert isinstance(result, int)
        assert 0 <= result < 10

    def test_builtin_rand_range(self):
        result = run_agent("rand(1, 10)")
        assert isinstance(result, int)
        assert 1 <= result <= 10

    def test_builtin_env_get(self):
        result = run_agent('env("get", "PATH")')
        assert result is not None

    def test_builtin_env_no_args(self):
        result = run_agent("let e = env()\ne.get('PATH')")
        assert result is not None

    def test_builtin_path_join(self):
        result = run_agent('path("join", "/tmp", "file.txt")')
        assert result == os.path.join("/tmp", "file.txt")

    def test_builtin_path_dirname(self):
        result = run_agent('path("dirname", "/tmp/file.txt")')
        assert result == "/tmp"

    def test_builtin_path_basename(self):
        result = run_agent('path("basename", "/tmp/file.txt")')
        assert result == "file.txt"

    def test_builtin_path_no_args(self):
        result = run_agent("let p = path()\np.join('a', 'b')")
        assert result == os.path.join("a", "b")

    def test_builtin_base64_encode(self):
        result = run_agent('base64("encode", "hello")')
        assert isinstance(result, str)
        import base64 as b64
        assert b64.b64decode(result).decode() == "hello"

    def test_builtin_base64_decode(self):
        import base64 as b64
        encoded = b64.b64encode(b"hello").decode()
        result = run_agent(f'base64("decode", "{encoded}")')
        assert result == "hello"

    def test_builtin_base64_no_args(self):
        result = run_agent("let b = base64()\nb.encode('test')")
        assert isinstance(result, str)

    def test_builtin_hash_sha256(self):
        result = run_agent('hash("sha256", "hello")')
        assert isinstance(result, str)
        assert len(result) == 64

    def test_builtin_hash_md5(self):
        result = run_agent('hash("md5", "hello")')
        assert isinstance(result, str)
        assert len(result) == 32

    def test_builtin_regex_match(self):
        result = run_agent('let r = regex()\nr.match("\\\\d+", "abc123def")')
        assert result is not None

    def test_builtin_regex_replace(self):
        result = run_agent('let r = regex()\nr.replace("a", "X", "abcabc")')
        assert result == "XbcXbc"


class TestInterpreterSkillPresets:
    def test_skill_math_add(self):
        result = run_agent("skill.load('math')\nskill.math.add(3, 4)")
        assert result == 7

    def test_skill_math_avg(self):
        result = run_agent("skill.load('math')\nskill.math.avg(1, 2, 3, 4, 5)")
        assert result == 3.0

    def test_skill_math_sqrt(self):
        result = run_agent("skill.load('math')\nskill.math.sqrt(16)")
        assert result == 4.0

    def test_skill_math_clamp(self):
        result = run_agent("skill.load('math')\nskill.math.clamp(15, 0, 10)")
        assert result == 10

    def test_skill_text_upper(self):
        result = run_agent("skill.load('text')\nskill.text.upper('hello')")
        assert result == "HELLO"

    def test_skill_text_lower(self):
        result = run_agent("skill.load('text')\nskill.text.lower('HELLO')")
        assert result == "hello"

    def test_skill_text_split(self):
        result = run_agent("skill.load('text')\nskill.text.split('a,b,c', ',')")
        assert result == ["a", "b", "c"]

    def test_skill_text_join(self):
        result = run_agent("skill.load('text')\nskill.text.join(['a', 'b'], '-')")
        assert result == "a-b"

    def test_skill_text_reverse(self):
        result = run_agent("skill.load('text')\nskill.text.reverse('hello')")
        assert result == "olleh"

    def test_skill_data_keys(self):
        result = run_agent("skill.load('data')\nskill.data.keys({'a': 1, 'b': 2})")
        assert sorted(result) == ["a", "b"]

    def test_skill_data_values(self):
        result = run_agent("skill.load('data')\nskill.data.values({'a': 1, 'b': 2})")
        assert sorted(result) == [1, 2]

    def test_skill_data_first(self):
        result = run_agent("skill.load('data')\nskill.data.first([1, 2, 3])")
        assert result == 1

    def test_skill_data_last(self):
        result = run_agent("skill.load('data')\nskill.data.last([1, 2, 3])")
        assert result == 3

    def test_skill_data_chunk(self):
        result = run_agent("skill.load('data')\nskill.data.chunk([1, 2, 3, 4], 2)")
        assert result == [[1, 2], [3, 4]]

    def test_skill_data_pick(self):
        result = run_agent("skill.load('data')\nskill.data.pick({'a': 1, 'b': 2}, 'a')")
        assert result == {"a": 1}

    def test_skill_data_omit(self):
        result = run_agent("skill.load('data')\nskill.data.omit({'a': 1, 'b': 2}, 'a')")
        assert result == {"b": 2}

    def test_skill_list(self):
        result = run_agent("skill.load('math')\nskill.list()")
        assert "math" in result

    def test_skill_run(self):
        result = run_agent("skill.load('math')\nskill.run('math', {action: 'add', a: 3, b: 4})")
        assert result == 7


class TestInterpreterTestFramework:
    def test_test_registration(self):
        interp = Interpreter()
        lexer = Lexer('test "my test" { assert true }')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interp.interpret(ast)
        assert "my test" in interp.tests

    def test_suite_registration(self):
        interp = Interpreter()
        lexer = Lexer('suite "my suite" { test "t1" { assert true } }')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interp.interpret(ast)
        assert "my suite" in interp.suites


class TestInterpreterAsync:
    def test_async_block(self):
        result = run_agent("async { 42 }")
        assert result == 42

    def test_async_with_variable(self):
        result = run_agent("async { let x = 10\nx + 5 }")
        assert result == 15


class TestInterpreterParallel:
    def test_parallel_block(self):
        result = run_agent("parallel { let a = 1 let b = 2 }")
        assert isinstance(result, list)

    def test_wait_all(self):
        result = run_agent("let a = 1\nlet b = 2\nwait(all) [a, b]")
        assert result == [1, 2]

    def test_wait_any(self):
        result = run_agent("let a = 1\nlet b = 2\nwait(any) [a, b]")
        assert result == 1


class TestInterpreterCmdModule:
    def test_cmd_run(self):
        result = run_agent("cmd.run('echo hello')")
        assert result.stdout.strip() == "hello"

    def test_cmd_run_timeout(self):
        result = run_agent("cmd.run('sleep 100', 0.1)")
        assert result.success is False

    def test_cmd_which(self):
        result = run_agent("cmd.which('python3')")
        assert result.found is True

    def test_cmd_exists(self):
        result = run_agent("cmd.exists('python3')")
        assert result is True

    def test_cmd_which_not_found(self):
        result = run_agent("cmd.which('nonexistent_cmd_xyz')")
        assert result.found is False

    def test_cmd_exists_not_found(self):
        result = run_agent("cmd.exists('nonexistent_cmd_xyz')")
        assert result is False

    def test_cmd_platform(self):
        result = run_agent("cmd.platform.system")
        assert result is not None

    def test_cmd_shell_user(self):
        result = run_agent("cmd.shell.user")
        assert result is not None

    def test_cmd_cwd(self):
        result = run_agent("cmd.cwd")
        assert isinstance(result, str)

    def test_cmd_home(self):
        result = run_agent("cmd.home")
        assert isinstance(result, str)

    def test_cmd_tmpdir(self):
        result = run_agent("cmd.tmpdir")
        assert isinstance(result, str)

    def test_cmd_env(self):
        result = run_agent("cmd.env")
        assert isinstance(result, dict)

    def test_cmd_path_list(self):
        result = run_agent("cmd.path")
        assert isinstance(result, list)

    def test_cmd_getenv(self):
        result = run_agent("cmd.getenv('PATH')")
        assert result is not None


class TestInterpreterLLMModule:
    def test_llm_no_args(self):
        result = run_agent("llm.prompt('hello')")
        assert result == "LLM response"

    def test_llm_new(self):
        result = run_agent("let l = llm.new({provider: 'openai', model: 'gpt-4'})\nl.provider")
        assert result == "openai"

    def test_llm_chat(self):
        result = run_agent("llm.chat('hello')")
        assert hasattr(result, 'content')
        assert result.content == "LLM response"


class TestInterpreterKBModule:
    def test_kb_connect(self):
        result = run_agent("kb.connect('test', {})")
        assert result is None

    def test_kb_search(self):
        result = run_agent("kb.search('query')")
        assert result == []


class TestInterpreterMCPModule:
    def test_mcp_list_tools(self):
        result = run_agent("mcp.list_tools()")
        assert result == []

    def test_mcp_connect(self):
        result = run_agent("mcp.connect('http://localhost')")
        assert result is None

    def test_mcp_call_tool(self):
        result = run_agent("mcp.call_tool('tool', {})")
        assert result == {}


class TestInterpreterAPIModule:
    def test_api_module_created(self):
        result = run_agent("api")
        assert hasattr(result, "call")
        assert hasattr(result, "get")
        assert hasattr(result, "post")


class TestInterpreterLogModule:
    def test_log_info(self, capsys):
        run_agent("log.info('test message')")
        captured = capsys.readouterr()
        assert "[INFO] test message" in captured.out

    def test_log_debug(self, capsys):
        run_agent("log.debug('debug message')")
        captured = capsys.readouterr()
        assert "[DEBUG] debug message" in captured.out

    def test_log_warn(self, capsys):
        run_agent("log.warn('warning')")
        captured = capsys.readouterr()
        assert "[WARN] warning" in captured.out

    def test_log_error(self, capsys):
        run_agent("log.error('error')")
        captured = capsys.readouterr()
        assert "[ERROR] error" in captured.out


class TestInterpreterInputModule:
    def test_input_module_no_args(self):
        result = run_agent("input.args()")
        assert isinstance(result, list)


class TestInterpreterOutputModule:
    def test_output_file(self, tmp_path):
        filepath = str(tmp_path / "test_output.txt")
        run_agent(f'output.file("{filepath}", "hello world")')
        with open(filepath, "r") as f:
            assert f.read() == "hello world"


class TestInterpreterImport:
    def test_import_module(self, tmp_path):
        mod_file = tmp_path / "mymod.agent"
        mod_file.write_text("function double(x) { return x * 2 }")
        result = run_agent(f'import "{mod_file}"\ndouble(5)')
        assert result == 10

    def test_import_as(self, tmp_path):
        mod_file = tmp_path / "util.agent"
        mod_file.write_text('let VERSION = "1.0"')
        result = run_agent(f'import "{mod_file}" as util\nutil.VERSION')
        assert result == "1.0"

    def test_from_import(self, tmp_path):
        mod_file = tmp_path / "mylib.agent"
        mod_file.write_text("function square(x) { return x * x }\nlet PI = 3.14")
        result = run_agent(f'from "{mod_file}" import square, PI\nsquare(5)')
        assert result == 25


class TestInterpreterAssertEq:
    def test_assert_eq_true(self):
        result = run_agent("assert_eq(1, 1)")
        assert result is True

    def test_assert_eq_false(self):
        with pytest.raises(AssertionError):
            run_agent("assert_eq(1, 2)")

    def test_assert_eq_strings(self):
        result = run_agent('assert_eq("hello", "hello")')
        assert result is True


class TestInterpreterHigherOrderFunctions:
    def test_builtin_filter(self):
        result = run_agent("let lst = [1, 2, 3, 4, 5]\nfunction is_odd(x) { return x % 2 != 0 }\nfilter(is_odd, lst)")
        assert result == [1, 3, 5]

    def test_builtin_map(self):
        result = run_agent("let lst = [1, 2, 3]\nfunction double(x) { return x * 2 }\nmap(double, lst)")
        assert result == [2, 4, 6]

    def test_builtin_reduce(self):
        result = run_agent("let lst = [1, 2, 3, 4]\nfunction sum(a, b) { return a + b }\nreduce(sum, lst)")
        assert result == 10


class TestInterpreterEdgeCases:
    def test_multiple_statements(self):
        result = run_agent("let a = 1\nlet b = 2\na + b")
        assert result == 3

    def test_deeply_nested(self):
        result = run_agent("((((1 + 2) * 3) - 4) / 5)")
        assert result == 1.0

    def test_string_in_list(self):
        result = run_agent('["a", "b", "c"][1]')
        assert result == "b"

    def test_dict_in_list(self):
        result = run_agent('[{"a": 1}][0]["a"]')
        assert result == 1

    def test_method_call_on_string(self):
        result = run_agent("skill.load('text')\nskill.text.upper('hello')")
        assert result == "HELLO"


class TestRunFile:
    def test_run_file(self, tmp_path):
        test_file = tmp_path / "test.agent"
        test_file.write_text("let x = 10\nx + 5")
        result = run_file(str(test_file))
        assert result == 15


class TestAFLObject:
    def test_afl_object_creation(self):
        obj = AFLObject(x=1, y=2)
        assert obj.x == 1
        assert obj.y == 2

    def test_afl_object_dynamic_attr(self):
        obj = AFLObject()
        obj.foo = "bar"
        assert obj.foo == "bar"


class TestSkillModule:
    def test_skill_module_load(self):
        interp = Interpreter()
        skill_mod = SkillModule(interp)
        result = skill_mod.load("math")
        assert result is not None

    def test_skill_module_run(self):
        interp = Interpreter()
        skill_mod = SkillModule(interp)
        skill_mod.load("math")
        result = skill_mod.run("math", {"action": "add", "a": 1, "b": 2})
        assert result == 3

    def test_skill_module_list(self):
        interp = Interpreter()
        skill_mod = SkillModule(interp)
        skill_mod.load("math")
        result = skill_mod.list()
        assert "math" in result

    def test_skill_module_getattr(self):
        interp = Interpreter()
        skill_mod = SkillModule(interp)
        math_mod = skill_mod.load("math")
        assert math_mod.add(1, 2) == 3

    def test_skill_module_getitem(self):
        interp = Interpreter()
        skill_mod = SkillModule(interp)
        math_mod = skill_mod["math"]
        assert math_mod.add(3, 4) == 7

    def test_skill_module_import_alias(self):
        interp = Interpreter()
        skill_mod = SkillModule(interp)
        result = skill_mod.import_skill("math")
        assert result is not None
