# AgentFlow Language (AFL) v1.6 文档

## 1. 简介

AgentFlow Language (AFL) 是一门专为 Agent 开发设计的领域特定语言 (DSL)，支持声明式和命令式混合编程。内置 LLM 调用、知识库检索、MCP 协议、系统命令、异步并发等能力。

## 1.1 最近更新 (v1.6)

- **全面测试覆盖**: 新增 425 个 Python 单元测试，覆盖词法分析、语法解析、AST 节点、解释器、CLI 全链路
  - `tests/test_lexer.py` — 词法分析器测试 (64 项)
  - `tests/test_parser.py` — 语法解析器测试 (53 项)
  - `tests/test_nodes.py` — AST 节点测试 (40 项)
  - `tests/test_interpreter.py` — 解释器测试 (257 项)
  - `tests/test_agent.py` — CLI 入口及集成测试 (11 项)
- **Bug 修复**:
  - 修复词法分析器 `skip_whitespace()` 列号重复计数问题
  - 修复逻辑运算符 `&&`/`||` 在 AST 中未转换为 `and`/`or` 的问题
  - 修复 `wait(all)` 括号语法解析支持
  - 修复导入模块无法通过名称查找的问题 (`_get_var`)
  - 修复 `filter`/`map`/`reduce` 高阶函数传参方式
  - 修复 `regex.replace` 参数顺序错误
- **Skill 模块重磅升级**:

- **Skill 模块重磅升级**: 
  - 新增 3 大内置预设 skill：`math`（16 方法）、`text`（17 方法）、`data`（16 方法）
  - `skill.load(name)` 支持导入 `.agent` / `.afl` 文件作为 skill
  - `skill.run(name, opts)` 运行时动态调用
  - `skill.list()` 列出已导入 skills
  - `skill.<name>.<method>()` 和 `skill["name"]` 双模式访问
  - 自动 lazy import：首次访问时自动加载
- **内存管理优化**: SkillModule 实例缓存，避免重复创建

## 2. 安装和使用

### 2.1 安装

```bash
cd /path/to/agent-lang
```

### 2.2 运行

```bash
python3 afl_lang/agent.py examples/hello.agent
```

REPL 模式:

```bash
python3 afl_lang/agent.py repl
```

Python API:

```python
from afl_lang import run_agent, run_file

# 运行代码字符串
run_agent('print("Hello, World!")')

# 运行文件
run_file("examples/hello.agent")
```

## 3. 基础语法

### 3.1 变量与类型

```afl
let name = "Alice"              # 字符串
let count = 10                  # 数字
let rate = 3.14                 # 浮点数
let active = true               # 布尔值
let items = [1, 2, 3]          # 列表
let config = { "timeout": 30 }  # 字典
let empty = null                # 空值
```

### 3.2 运算符

- 算术: `+`, `-`, `*`, `/`, `%`, `**`
- 比较: `==`, `!=`, `<`, `>`, `<=`, `>=`
- 逻辑: `and`, `or`, `not`
- 字符串拼接: `+`
- 索引访问: `obj[index]` 或 `dict["key"]`
- 空值合并: `??`
- 成员检查: `in`

```afl
let x = 10 + 5
let y = x ** 2
let is_valid = x > 0 and x < 100
let msg = "Hello, " + name

# 索引访问
let items = [1, 2, 3]
print(items[0])          # 1
let dict = { "a": 1, "b": 2 }
print(dict["a"])         # 1
```

### 3.3 条件分支

```afl
if count >= 10 {
    print("high")
} else if count >= 5 {
    print("medium")
} else {
    print("low")
}

# 三元表达式
let level = if count >= 10 then "high" else "low"
```

### 3.4 循环

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

### 3.5 函数

```afl
function add(a, b) {
    return a + b
}

# 带返回类型声明
function greet(name) -> string {
    return "Hello, " + name + "!"
}

# 带类型注解的参数
function process(items: list, options: dict) -> dict {
    return { "result": items, "count": len(items) }
}

let result = add(3, 5)

# 关键字参数
function greet_user(name, greeting="Hello") -> string {
    return greeting + ", " + name + "!"
}
let msg = greet_user("Alice", greeting="Hi")  # "Hi, Alice!"
```

### 3.6 异步与并发

```afl
# 异步代码块
async {
    let result = await llm.prompt("Hello")
    print(result)
}

# 并行执行
parallel {
    let a = api.call("GET", "https://api1.example.com")
    let b = api.call("GET", "https://api2.example.com")
}
wait(all)  # 或 wait(any)
```

## 4. 内置函数

### 4.1 类型转换与数学

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

### 4.2 数据操作

```afl
len([1, 2, 3])   # 3
type("hello")     # "str"
range(5)          # [0, 1, 2, 3, 4]
range(1, 5)      # [1, 2, 3, 4]
append(items, 4)  # 添加元素
pop(items)        # 移除并返回最后元素
sort(items)       # 排序
filter(items, fn) # 过滤
map(items, fn)    # 映射
reduce(items, fn) # 归约
json(data)        # JSON 编解码
```

### 4.3 实用工具

```afl
time()            # 当前时间戳
uuid()            # 生成 UUID
rand()            # 随机数
regex(pattern, text) # 正则匹配
env("HOME")       # 读取环境变量
env("set", "KEY", "VAL")  # 设置环境变量
path("join", a, b)   # 路径拼接
path("dirname", p)   # 目录名
path("basename", p)  # 文件名
base64("encode", data) # Base64 编解码
hash("sha256", data)   # SHA256 哈希
hash("md5", data)      # MD5 哈希
```

### 4.4 输入输出

```afl
print("Hello")            # 打印
input.args()              # 命令行参数
input.prompt("name:")     # 交互输入
output.file("a.txt", x)   # 写入文件
```

### 4.5 系统命令 (cmd)

```afl
cmd.run("ls -la")         # 执行命令
cmd.platform.system       # 操作系统
cmd.platform.release      # 系统版本
cmd.platform.machine      # 架构
cmd.cwd                   # 当前目录
cmd.home                  # 家目录
cmd.tmpdir                # 临时目录
cmd.exists("python3")     # 命令是否存在
cmd.which("python3")      # 命令路径
cmd.type("ls")            # 命令类型
cmd.version("python3")    # 命令版本
```

### 4.6 网络请求 (api)

```afl
api.call("GET", "https://api.example.com")
api.call("POST", url, { body: data, headers: {...} })
```

### 4.7 LLM 调用 (llm)

```afl
llm.new({ provider: "openai", model: "gpt-4" })
llm.prompt("Tell a joke")
```

### 4.8 知识库 (kb)

```afl
kb.connect("local", { path: "./kb" })
let results = kb.search("password reset", top_k=3)
# top_k: 返回结果数量 (关键字参数)
```

### 4.9 MCP 协议 (mcp)

```afl
mcp.connect("http://localhost:8080")
mcp.list_tools()
mcp.call_tool("tool_name", { arg: value })
```

### 4.10 Skill 模块 (skill)

内置预设技能，开箱即用；也支持从 `.agent` / `.afl` 文件导入。

```afl
# ── 内置预设 skill（自动导入） ──

# math 技能
skill.math.add(10, 20)                    # 30
skill.math.avg(10, 20, 30)                # 20.0
skill.math.clamp(150, 0, 100)             # 100
skill.math.sqrt(16)                       # 4.0
skill.math.pow(2, 10)                     # 1024

# text 技能
skill.text.upper("hello")                 # "HELLO"
skill.text.split("a,b,c", ",")            # ["a", "b", "c"]
skill.text.join(["x", "y"], "|")          # "x|y"
skill.text.pad_left("42", 5, "0")         # "00042"
skill.text.reverse("abc")                 # "cba"

# data 技能
skill.data.keys({ "a": 1, "b": 2 })       # ["a", "b"]
skill.data.pick(user, "name", "age")      # {"name": ..., "age": ...}
skill.data.omit(config, "secret")         # 排除指定 key
skill.data.chunk([1,2,3,4,5], 2)          # [[1,2],[3,4],[5]]
skill.data.merge(dict1, dict2)            # 合并多个字典

# ── 文件 skill 导入 ──
skill.load("examples/string_utils.afl")
skill["examples/string_utils.afl"].title_case("hello world")

# ── 运行时调用 ──
skill.run("math", { action: "add", a: 100, b: 200 })   # 300
skill.list()                                             # ["math", "text", ...]
```

### 4.11 日志 (log)

```afl
log.info("message")
log.debug("debug")
log.warn("warning")
log.error("error")
```

### 4.12 测试 (test)

```afl
test "should add correctly" {
    assert add(2, 3) == 5
}
test.run()       # 运行所有测试
test.run("name") # 运行指定测试
```

## 5. 错误处理

### 5.1 基本错误处理

```afl
try {
    let resp = api.call("GET", "https://api.example.com")
} catch error {
    print("Error: " + error)
} finally {
    print("cleanup")
}
```

### 5.2 抛出异常

```afl
if x < 0 {
    throw "x must be non-negative"
}
```

### 5.3 异步错误处理

```afl
async {
    try {
        let result = await llm.prompt("Hello")
    } catch err {
        print("LLM error: " + err)
    }
}
```

## 6. 模块系统

### 6.1 导入模块

```afl
import "./utils.afl" as utils
print(utils.add(3, 5))
```

### 6.2 部分导入

```afl
from "./math.afl" import add, sub
print(add(3, 5))
```

### 6.3 导出

```afl
function helper() { return 42 }
export helper
```

## 7. 测试

```afl
test "should add correctly" {
    assert add(2, 3) == 5
}

test "should handle strings" {
    assert "hello" + " world" == "hello world"
}

test.run()       # 运行所有测试
test.run("name") # 运行指定测试
```

## 8. 示例

### 8.1 Hello World

```afl
let name = "Alice"
print("Hello, " + name + "!")
```

### 8.2 计算器

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

### 8.3 API 调用与重试

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

### 8.4 系统命令研究

```afl
print("Platform: " + cmd.platform.system + " " + cmd.platform.release)
print("Python: " + cmd.platform.python)
print("User: " + cmd.shell.user)

if cmd.exists("git") {
    print("Git version: " + cmd.version("git"))
}
```

### 8.6 Q&A 智能问答

```afl
let question = input.args()[0] ?? input.prompt("Ask me anything:")

# 连接知识库（模拟）
kb.connect("local", { path: "./kb" })
let references = kb.search(question, top_k=3)

# 构造提示
let prompt = """
Context: {{refs}}
Question: {{q}}
Answer concisely based on context.
"""

# 调用 LLM（模拟）
llm.new({ provider: "anthropic", model: "claude-3" })
let answer = llm.prompt(prompt, { refs: references, q: question })

print(answer)
output.file("answer.txt", answer)
```

## 9. 保留字

```
# 控制流
if, else, elseif, for, in, while, break, continue

# 函数与模块
function, return, import, from, export, test, suite

# 错误处理
try, catch, finally, throw

# 异步
async, await, parallel, wait

# 逻辑
and, or, not

# 值
true, false, null
```

## 10. 项目结构

```
agent-lang/
├── afl_lang/              # 核心解释器
│   ├── __init__.py        # 解释器实现
│   ├── lexer.py           # 词法分析器
│   ├── parser.py          # 语法分析器
│   ├── nodes.py           # AST 节点定义
│   └── agent.py           # 入口脚本
├── tests/                 # Python 单元测试 (425 项)
│   ├── test_lexer.py      # 词法分析器测试
│   ├── test_parser.py     # 语法解析器测试
│   ├── test_nodes.py      # AST 节点测试
│   ├── test_interpreter.py # 解释器测试
│   └── test_agent.py      # CLI 及集成测试
├── examples/              # 示例代码
│   ├── hello.agent        # Hello World
│   ├── cmd_demo.agent     # 系统命令演示
│   └── ...
└── README.md              # 本文档
```

## 11. 运行测试

```bash
python3 -m pytest tests/ -v
```

## 12. 联系方式

- 版本: v1.6