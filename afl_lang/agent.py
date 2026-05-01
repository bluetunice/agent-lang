import sys
import os

# 动态添加项目根目录到 sys.path，避免硬编码路径
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from afl_lang import run_file, repl


if len(sys.argv) > 1:
    if sys.argv[1] == "repl":
        repl()
    else:
        run_file(sys.argv[1])
else:
    print("AgentFlow Language (AFL) Interpreter v1.1")
    print("Usage: python3 afl_lang/agent.py <file.agent>")
    print("       python3 afl_lang/agent.py repl")