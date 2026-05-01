// AgentFlow Language (AFL) - Website JS v1.5

document.addEventListener('DOMContentLoaded', () => {

  // ---- Mobile menu toggle ----
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }

  // ---- Scroll-triggered animations ----
  const fadeEls = document.querySelectorAll('.fade-in');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });
  fadeEls.forEach(el => observer.observe(el));

  // ---- Syntax tabs ----
  const tabs = document.querySelectorAll('.syntax-tab');
  const panels = document.querySelectorAll('.syntax-panel');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById(`panel-${target}`);
      if (panel) panel.classList.add('active');
    });
  });

  // ---- Playground examples data ----
  const EXAMPLES = {
    hello: `let name = "World"
print("Hello, " + name + "!")

let items = [1, 2, 3]
for i in items {
    print("Item: " + str(i))
}

print("Done!")`,
    fizzbuzz: `for i in range(1, 16) {
    if i % 15 == 0 {
        print("FizzBuzz")
    } else if i % 3 == 0 {
        print("Fizz")
    } else if i % 5 == 0 {
        print("Buzz")
    } else {
        print(str(i))
    }
}`,
    fibonacci: `function fib(n) {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}

for i in range(10) {
    print("fib(" + str(i) + ") = " + str(fib(i)))
}`,
    api: `# API 调用示例
# 需要后端 AFL 运行时支持真实 HTTP
let url = "https://httpbin.org/get"

try {
    let resp = api.call("GET", url, { timeout: 10 })
    print("Status: " + str(resp.status))
    print("Body: " + str(resp.body))
} catch err {
    print("API Error: " + str(err))
    print("(API calls require a backend interpreter)")
}`,
    cmd: `# 系统命令示例
print("Platform: " + cmd.platform.system + " " + cmd.platform.release)
print("Machine: " + cmd.platform.machine)
print("Current dir: " + cmd.cwd)
print("Python: " + cmd.platform.python)

if cmd.exists("python3") {
    print("Python3 path: " + cmd.which("python3"))
}`,
    sort: `let numbers = [42, 7, 19, 3, 88, 15, 64]
print("Before: " + str(numbers))
sort(numbers)
print("After:  " + str(numbers))

let names = ["Bob", "Alice", "Charlie", "David"]
sort(names)
print("Names:  " + str(names))

print("Max: " + str(max(numbers)))
print("Min: " + str(min(numbers)))
print("Sum: " + str(reduce(numbers, fn)))`,
    skill: `# Skill 技能系统示例
print("=== Skill 演示 ===")

# math 预设 skill
print("math.add(10, 20) = " + str(skill.math.add(10, 20)))
print("math.avg(10, 20, 30) = " + str(skill.math.avg(10, 20, 30)))
print("math.clamp(150, 0, 100) = " + str(skill.math.clamp(150, 0, 100)))
print("math.sqrt(16) = " + str(skill.math.sqrt(16)))

# text 预设 skill
print("text.upper('hello') = " + skill.text.upper("hello"))
print("text.pad_left('42', 5, '0') = " + skill.text.pad_left("42", 5, "0"))
print("text.reverse('abc') = " + skill.text.reverse("abc"))

# data 预设 skill
let data = { "name": "Alice", "age": 30, "city": "Beijing" }
print("data.keys: " + str(skill.data.keys(data)))
print("data.pick: " + str(skill.data.pick(data, "name", "age")))

# 列表
print("skill.list(): " + str(skill.list()))
print("=== Skill 演示完成 ===")`
  };

  // ---- Playground ----
  const runBtn = document.getElementById('run-btn');
  const playInput = document.getElementById('play-input');
  const playOutput = document.getElementById('play-output');
  const statusEl = document.getElementById('status');
  const clearBtn = document.getElementById('clear-btn');
  const exampleBtn = document.getElementById('example-btn');

  function setStatus(msg, isError) {
    if (statusEl) {
      statusEl.textContent = msg;
      statusEl.style.color = isError ? '#ef4444' : '#10b981';
    }
  }

  if (runBtn && playInput) {
    runBtn.addEventListener('click', async () => {
      const code = playInput.value;
      if (!code.trim()) {
        playOutput.textContent = '// Enter some AFL code above';
        setStatus('请输入代码', true);
        return;
      }
      playOutput.textContent = '// Running...';
      setStatus('运行中...');

      try {
        const resp = await fetch('/api/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code }),
        });
        if (resp.ok) {
          const data = await resp.json();
          playOutput.textContent = data.output || data.error || '// (no output)';
          setStatus(data.error ? '错误' : '完成');
        } else {
          playOutput.textContent = '// Error: Could not reach AFL runtime';
          setStatus('无法连接到运行时', true);
        }
      } catch (e) {
        playOutput.textContent = `// Running AFL requires a backend interpreter.
// Install: python3 afl_lang/agent.py repl
//
// Your code:
${code}`;
        setStatus('离线模式（仅显示代码）', true);
      }
    });
  }

  if (clearBtn && playInput) {
    clearBtn.addEventListener('click', () => {
      playInput.value = '';
      playOutput.textContent = '// Editor cleared';
      setStatus('已清空');
    });
  }

  if (exampleBtn && playInput && playOutput) {
    exampleBtn.addEventListener('click', () => {
      const chips = document.querySelectorAll('.example-chip');
      if (chips.length > 0) {
        chips[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        chips[0].focus();
      }
    });
  }

  // ---- Example chips ----
  document.querySelectorAll('.example-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const key = chip.dataset.example;
      const code = EXAMPLES[key];
      if (code && playInput) {
        playInput.value = code;
        playOutput.textContent = '// Code loaded. Click "Run" to execute.';
        setStatus(`已加载示例: ${chip.textContent}`);
      }
    });
  });

  // ---- Sidebar active section highlight ----
  const sidebarLinks = document.querySelectorAll('.docs-sidebar a');
  if (sidebarLinks.length > 0) {
    const sections = document.querySelectorAll('.docs-content h2[id], .docs-content h3[id]');
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          sidebarLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
          });
        }
      });
    }, { threshold: 0.3 });
    sections.forEach(s => sectionObserver.observe(s));
  }

  // ---- Copy code buttons ----
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = btn.closest('.code-block').querySelector('.code-body');
      if (!code) return;
      const text = code.textContent;
      navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
      });
    });
  });
});
