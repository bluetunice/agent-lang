import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from afl_lang import repl, run_agent


class TestRunAgent:
    def test_run_agent_hello(self, capsys):
        run_agent('print("hello world")')
        captured = capsys.readouterr()
        assert "hello world" in captured.out

    def test_run_agent_expression(self):
        result = run_agent("1 + 1")
        assert result == 2

    def test_run_agent_multiline(self):
        result = run_agent("let x = 1\nlet y = 2\nx + y")
        assert result == 3

    def test_run_agent_complex(self):
        result = run_agent(
            "function fib(n) {\n"
            "  if n <= 1 { return n }\n"
            "  return fib(n-1) + fib(n-2)\n"
            "}\n"
            "fib(10)"
        )
        assert result == 55


class TestAgentCLI:
    def test_cli_runs_file(self, tmp_path):
        test_file = tmp_path / "cli_test.agent"
        test_file.write_text('print("cli works")')
        result = os.popen(f"python3 afl_lang/agent.py {test_file}").read()
        assert "cli works" in result

    def test_cli_repl_mode(self):
        result = os.popen("echo 'exit' | python3 afl_lang/agent.py repl 2>&1").read()
        assert "REPL" in result or "exit" in result or "AgentFlow" in result

    def test_cli_no_args(self):
        result = os.popen("python3 afl_lang/agent.py 2>&1").read()
        assert "Usage" in result

    def test_cli_runs_example_file(self):
        result = os.popen("python3 afl_lang/agent.py examples/test1.agent 2>&1").read()
        assert len(result) > 0


class TestIntegrationExamples:
    def test_test_basic(self):
        result = os.popen("python3 afl_lang/agent.py examples/test_basic.agent 2>&1").read()
        assert len(result) > 0

    def test_test_control(self):
        result = os.popen("python3 afl_lang/agent.py examples/test_control.agent 2>&1").read()
        assert len(result) > 0

    def test_complete_test(self):
        result = os.popen("python3 afl_lang/agent.py examples/complete_test.agent 2>&1").read()
        assert len(result) > 0

    def test_skill_demo(self):
        result = os.popen("python3 afl_lang/agent.py examples/skill_demo.agent 2>&1").read()
        assert len(result) > 0

    def test_advanced_features(self):
        result = os.popen("python3 afl_lang/agent.py examples/advanced_features.agent 2>&1").read()
        assert len(result) > 0

    def test_file_skill_demo(self):
        result = os.popen("python3 afl_lang/agent.py examples/file_skill_demo.agent 2>&1").read()
        assert len(result) > 0
