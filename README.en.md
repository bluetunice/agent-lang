# AgentFlow Language (AFL) v1.6 Documentation

## 1. Introduction

AgentFlow Language (AFL) is a domain-specific language (DSL) designed specifically for Agent development, supporting both declarative and imperative hybrid programming. Built-in capabilities include LLM invocation, knowledge base retrieval, MCP protocol, system commands, and async concurrency.

## 1.1 Recent Updates (v1.6)

- **Comprehensive Test Coverage**: Added 425 Python unit tests covering lexical analysis, parsing, AST nodes, interpreter, and CLI end-to-end.
  - `tests/test_lexer.py` — Lexer tests (64 cases)
  - `tests/test_parser.py` — Parser tests (53 cases)
  - `tests/test_nodes.py` — AST node tests (40 cases)
  - `tests/test_interpreter.py` — Interpreter tests (257 cases)
  - `tests/test_agent.py` — CLI and integration tests (11 cases)
- **Bug Fixes**:
  - Fixed lexer `skip_whitespace()` column number double-counting issue
  - Fixed logical operators `&&`/`||` not being converted to `and`/`or` in AST
  - Fixed `wait(all)` bracket syntax parsing support
  - Fixed imported modules not being resolvable by name (`_get_var`)
  - Fixed `filter`/`map`/`reduce` higher-order function argument passing
  - Fixed `regex.replace` parameter order error
- **Skill Module Major Upgrade**:

- **Skill Module Major Upgrade**:
  - Added 3 built-in preset skills: `math` (16 methods), `text` (17 methods), `data` (16 methods)
  - `skill.load(name)` supports importing `.agent` / `.afl` files as skills
  - `skill.run(name, opts)` for runtime dynamic invocation
  - `skill.list()` lists loaded skills
  - `skill.<name>.<method>()` and `skill["name"]` dual access modes
  - Automatic lazy import on first access
- **Memory Management Optimization**: SkillModule instance caching to avoid duplicate creation

## 2. Installation and Usage

### 2.1 Installation

```bash
cd /path/to/agent-lang
```

### 2.2 Running

```bash
python3 afl_lang/agent.py examples/hello.agent
```

REPL mode:

```bash
python3 afl_lang/agent.py repl
```

Python API:

```python
from afl_lang import run_agent, run_file

# Run code string
run_agent('print("Hello, World!")')

# Run file
run_file("examples/hello.agent")
```

## 3. Basic Syntax

### 3.1 Variables and Types

```afl
let name = "Alice"              # String
let count = 10                  # Number
let rate = 3.14                 # Float
let active = true               # Boolean
let items = [1, 2, 3]          # List
let config = { "timeout": 30 }  # Dict
let empty = null                # Null
```

### 3.2 Operators

- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`
- String concatenation: `+`
- Index access: `obj[index]` or `dict["key"]`
- Null coalescing: `??`
- Membership check: `in`

```afl
let x = 10 + 5
let y = x ** 2
let is_valid = x > 0 and x < 100
let msg = "Hello, " + name

# Index access
let items = [1, 2, 3]
print(items[0])          # 1
let dict = { "a": 1, "b": 2 }
print(dict["a"])         # 1
```

### 3.3 Conditionals

```afl
if count >= 10 {
    print("high")
} else if count >= 5 {
    print("medium")
} else {
    print("low")
}

# Ternary expression
let level = if count >= 10 then "high" else "low"
```

### 3.4 Loops

```afl
for i in range(5) {
    print(i)
}

for item in items {
    print(item)
}

while x > 0 {
    x = x - 1
}
```

### 3.5 Functions

```afl
function add(a, b) {
    return a + b
}

# With return type declaration
function greet(name) -> string {
    return "Hello, " + name + "!"
}

# With type annotations
function process(items: list, options: dict) -> dict {
    return { "result": items, "count": len(items) }
}

let result = add(3, 5)

# Keyword arguments
function greet_user(name, greeting="Hello") -> string {
    return greeting + ", " + name + "!"
}
let msg = greet_user("Alice", greeting="Hi")  # "Hi, Alice!"
```

### 3.6 Async and Concurrency

```afl
# Async block
async {
    let result = await llm.prompt("Hello")
    print(result)
}

# Parallel execution
parallel {
    let a = api.call("GET", "https://api1.example.com")
    let b = api.call("GET", "https://api2.example.com")
}
wait(all)  # or wait(any)
```

## 4. Built-in Functions

### 4.1 Type Conversion and Math

```afl
str(123)        # "123"
int("42")       # 42
float("3.14")   # 3.14
bool(1)         # true
abs(-5)         # 5
round(3.7)      # 4
max(1, 5, 3)    # 5
min(1, 5, 3)   # 1
```

### 4.2 Data Operations

```afl
len([1, 2, 3])   # 3
type("hello")     # "str"
range(5)          # [0, 1, 2, 3, 4]
range(1, 5)      # [1, 2, 3, 4]
append(items, 4)  # Add element
pop(items)        # Remove and return last element
sort(items)       # Sort
filter(items, fn) # Filter
map(items, fn)    # Map
reduce(items, fn) # Reduce
json(data)        # JSON encode/decode
```

### 4.3 Utilities

```afl
time()            # Current timestamp
uuid()            # Generate UUID
rand()            # Random number
regex(pattern, text) # Regex match
env("HOME")       # Read environment variable
env("set", "KEY", "VAL")  # Set environment variable
path("join", a, b)   # Join paths
path("dirname", p)   # Directory name
path("basename", p)  # Base name
base64("encode", data) # Base64 encode/decode
hash("sha256", data)   # SHA256 hash
hash("md5", data)      # MD5 hash
```

### 4.4 Input and Output

```afl
print("Hello")            # Print
input.args()              # Command line arguments
input.prompt("name:")     # Interactive input
output.file("a.txt", x)   # Write to file
```

### 4.5 System Commands (cmd)

```afl
cmd.run("ls -la")         # Execute command
cmd.platform.system       # Operating system
cmd.platform.release      # OS version
cmd.platform.machine      # Architecture
cmd.cwd                   # Current directory
cmd.home                  # Home directory
cmd.tmpdir                # Temp directory
cmd.exists("python3")     # Check if command exists
cmd.which("python3")      # Find command path
cmd.type("ls")            # Command type
cmd.version("python3")    # Command version
```

### 4.6 Network Requests (api)

```afl
api.call("GET", "https://api.example.com")
api.call("POST", url, { body: data, headers: {...} })
```

### 4.7 LLM Invocation (llm)

```afl
llm.new({ provider: "openai", model: "gpt-4" })
llm.prompt("Tell a joke")
```

### 4.8 Knowledge Base (kb)

```afl
kb.connect("local", { path: "./kb" })
let results = kb.search("password reset", top_k=3)
# top_k: Number of results to return (keyword argument)
```

### 4.9 MCP Protocol (mcp)

```afl
mcp.connect("http://localhost:8080")
mcp.list_tools()
mcp.call_tool("tool_name", { arg: value })
```

### 4.10 Skill Module (skill)

Built-in preset skills ready to use; also supports importing from `.agent` / `.afl` files.

```afl
# ── Built-in preset skills (auto-imported) ──

# math skill
skill.math.add(10, 20)                    # 30
skill.math.avg(10, 20, 30)                # 20.0
skill.math.clamp(150, 0, 100)             # 100
skill.math.sqrt(16)                       # 4.0
skill.math.pow(2, 10)                     # 1024

# text skill
skill.text.upper("hello")                 # "HELLO"
skill.text.split("a,b,c", ",")            # ["a", "b", "c"]
skill.text.join(["x", "y"], "|")          # "x|y"
skill.text.pad_left("42", 5, "0")          # "00042"
skill.text.reverse("abc")                 # "cba"

# data skill
skill.data.keys({ "a": 1, "b": 2 })      # ["a", "b"]
skill.data.pick(user, "name", "age")      # {"name": ..., "age": ...}
skill.data.omit(config, "secret")            # Exclude specified keys
skill.data.chunk([1,2,3,4,5], 2)          # [[1,2],[3,4],[5]]
skill.data.merge(dict1, dict2)            # Merge multiple dicts

# ── File skill import ──
skill.load("examples/string_utils.afl")
skill["examples/string_utils.afl"].title_case("hello world")

# ── Runtime invocation ──
skill.run("math", { action: "add", a: 100, b: 200 })   # 300
skill.list()                                             # ["math", "text", ...]
```

### 4.11 Logging (log)

```afl
log.info("message")
log.debug("debug")
log.warn("warning")
log.error("error")
```

### 4.12 Testing (test)

```afl
test "should add correctly" {
    assert add(2, 3) == 5
}
test.run()       # Run all tests
test.run("name") # Run specific test
```

## 5. Error Handling

### 5.1 Basic Error Handling

```afl
try {
    let resp = api.call("GET", "https://api.example.com")
} catch error {
    print("Error: " + error)
} finally {
    print("cleanup")
}
```

### 5.2 Throwing Exceptions

```afl
if x < 0 {
    throw "x must be non-negative"
}
```

### 5.3 Async Error Handling

```afl
async {
    try {
        let result = await llm.prompt("Hello")
    } catch err {
        print("LLM error: " + err)
    }
}
```

## 6. Module System

### 6.1 Importing Modules

```afl
import "./utils.afl" as utils
print(utils.add(3, 5))
```

### 6.2 Partial Imports

```afl
from "./math.afl" import add, sub
print(add(3, 5))
```

### 6.3 Exports

```afl
function helper() { return 42 }
export helper
```

## 7. Testing

```afl
test "should add correctly" {
    assert add(2, 3) == 5
}

test "should handle strings" {
    assert "hello" + " world" == "hello world"
}

test.run()       # Run all tests
test.run("name") # Run specific test
```

## 8. Examples

### 8.1 Hello World

```afl
let name = "Alice"
print("Hello, " + name + "!")
```

### 8.2 Calculator

```afl
function add(a, b) { return a + b }
function sub(a, b) { return a - b }
function mul(a, b) { return a * b }
function div(a, b) { return a / b }

let a = 10
let b = 5
print(add(a, b))
print(sub(a, b))
print(mul(a, b))
print(div(a, b))
```

### 8.3 API Call with Retry

```afl
let max_retries = 3
let retry_count = 0

while retry_count < max_retries {
    try {
        let resp = api.call("GET", "https://api.example.com")
        if resp.status == 200 {
            print("Success!")
            break
        }
    } catch err {
        retry_count = retry_count + 1
        print("Retrying...")
    }
}
```

### 8.4 System Command Exploration

```afl
print("Platform: " + cmd.platform.system + " " + cmd.platform.release)
print("Python: " + cmd.platform.python)
print("User: " + cmd.shell.user)

if cmd.exists("git") {
    print("Git version: " + cmd.version("git"))
}
```

### 8.6 Q&A Intelligent Q&A

```afl
let question = input.args()[0] ?? input.prompt("Ask me anything:")

# Connect knowledge base (simulated)
kb.connect("local", { path: "./kb" })
let references = kb.search(question, top_k=3)

# Construct prompt
let prompt = """
Context: {{refs}}
Question: {{q}}
Answer concisely based on context.
"""

# Call LLM (simulated)
llm.new({ provider: "anthropic", model: "claude-3" })
let answer = llm.prompt(prompt, { refs: references, q: question })

print(answer)
output.file("answer.txt", answer)
```

## 9. Reserved Words

```
# Control flow
if, else, elseif, for, in, while, break, continue

# Functions and modules
function, return, import, from, export, test, suite

# Error handling
try, catch, finally, throw

# Async
async, await, parallel, wait

# Logical
and, or, not

# Values
true, false, null
```

## 10. Project Structure

```
agent-lang/
├── afl_lang/              # Core interpreter
│   ├── __init__.py        # Interpreter implementation
│   ├── lexer.py           # Lexer
│   ├── parser.py          # Parser
│   ├── nodes.py           # AST node definitions
│   └── agent.py           # Entry script
├── tests/                 # Python unit tests (425 cases)
│   ├── test_lexer.py      # Lexer tests
│   ├── test_parser.py     # Parser tests
│   ├── test_nodes.py      # AST node tests
│   ├── test_interpreter.py # Interpreter tests
│   └── test_agent.py      # CLI and integration tests
├── examples/              # Example code
│   ├── hello.agent        # Hello World
│   ├── cmd_demo.agent     # System command demo
│   └── ...
└── README.md              # This document
```

## 11. Running Tests

```bash
python3 -m pytest tests/ -v
```

## 12. Contact

- Version: v1.6