
- Prompt 构造器 (`builder.py`)
- ReAct 解析器 (`parser.py`)
- Ollama 客户端 (`client.py`)
- ReAct 引擎 (`react_engine.py`)
- 工具注册表 (`tool_registry.py`) 的**最小可运行版本**（方便你测试，实际使用时可被其他队员替换）
- 一个示例主程序 (`main.py`)

文件放入 `src/prompt/` 和 `src/core/` 等目录，直接运行测试。

---

## 📁 完整文件结构

```
src/
├── prompt/
│   ├── __init__.py
│   ├── builder.py
│   ├── parser.py
│   └── client.py
├── core/
│   └── react_engine.py
├── tools/
│   └── tool_registry.py
└── main.py (测试入口)
```

---

## 1️⃣ `src/prompt/builder.py`

```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ConversationTurn:
    role: str  # "user" or "assistant"
    content: str

class PromptBuilder:
    SYSTEM_PROMPT = """你是一个智能课程管理与规划助手，运行在 HKBU / COMP 课程体系下。

你具备以下核心能力：
1. 从课程知识库（RAG）中检索课程信息
2. 根据用户需求进行课程推荐、排课、冲突检测
3. 生成课表可视化图表
4. 回答课程政策、先修关系、学分、学期安排等问题

你必须严格遵循 ReAct 模式进行推理和行动，每一步输出格式如下：

Thought: <你当前对问题的理解>
Action: <你要调用的工具名称及参数，格式为 tool_name(param1=value1, param2=value2)>

注意：不要输出 Final Answer，只输出 Thought 和 Action。
当任务完成时，调用 stop() 工具，系统会自动输出最终答案。

## 可用工具（必须严格使用以下名称和参数）

1. rag_search(query: str, top_k: int = 5)
   - 功能：从课程向量库中检索相关信息
   - 示例：rag_search("COMP7095 先修课程")

2. optimize_schedule(course_list: list, constraints: dict)
   - 功能：排课优化，检测时间冲突，返回可行课表
   - 示例：optimize_schedule(["COMP7095", "COMP7125"], {"max_per_semester": 5})

3. generate_timetable(courses: list, format: str = "weekly")
   - 功能：生成课表图表（返回图片路径）
   - 示例：generate_timetable(["COMP7095", "COMP7115"], "weekly")

4. get_course_prerequisites(course_code: str)
   - 功能：返回某门课程的直接先修课程列表
   - 示例：get_course_prerequisites("COMP7095")

5. check_semester_availability(course_code: str, semester: str)
   - 功能：检查某课程在指定学期是否开设
   - 示例：check_semester_availability("COMP7095", "Semester 2")

6. stop()
   - 功能：终止当前任务，输出最终答案
   - 当所有必要信息已获取并可以回答用户时调用

## 课程限制条件（必须遵守）
- 学生必须先修完 **Prerequisites** 中的课程，才能选修后续课程
- 同一学期不建议选修超过 5 门课程
- 课程仅限 COMP / GCAP / GFHC 系列
- 若用户未指定专业，默认使用“MSc in IT Management”或“Creative Media”
- 若课程时间冲突，必须提示用户并建议调整

## 回答风格
- 必须基于 RAG 检索结果，不得编造课程信息
- 若信息不足，后续 Action 应继续检索或直接调用 stop() 并说明“无法确认”
"""

    @classmethod
    def build(cls,
              user_query: str,
              history: List[ConversationTurn] = None,
              rag_context: Optional[str] = None,
              max_history_turns: int = 5) -> str:
        prompt_parts = [cls.SYSTEM_PROMPT]

        if rag_context:
            prompt_parts.append(f"\n## 从课程库中检索到的相关信息\n{rag_context}\n")

        if history:
            history_text = "\n## 对话历史\n"
            for turn in history[-max_history_turns:]:
                if turn.role == "user":
                    history_text += f"用户：{turn.content}\n"
                else:
                    history_text += f"助手：{turn.content}\n"
            prompt_parts.append(history_text)

        prompt_parts.append(f"\n## 用户当前请求\n{user_query}\n")
        prompt_parts.append("""## 输出格式（严格遵守）
只输出以下两行，不要包含任何额外解释：

Thought: <你的推理>
Action: <工具调用，或 stop()>

Thought:""")

        return "\n".join(prompt_parts)

    @classmethod
    def build_final_answer_prompt(cls,
                                  user_query: str,
                                  rag_context: Optional[str] = None,
                                  history: List[ConversationTurn] = None,
                                  observations: List[str] = None) -> str:
        prompt_parts = [cls.SYSTEM_PROMPT]

        if rag_context:
            prompt_parts.append(f"\n## 从课程库中检索到的相关信息\n{rag_context}\n")

        if history:
            history_text = "\n## 对话历史\n"
            for turn in history:
                if turn.role == "user":
                    history_text += f"用户：{turn.content}\n"
                else:
                    history_text += f"助手：{turn.content}\n"
            prompt_parts.append(history_text)

        if observations:
            obs_text = "\n## 工具执行观察结果\n"
            for i, obs in enumerate(observations, 1):
                obs_text += f"{i}. {obs}\n"
            prompt_parts.append(obs_text)

        prompt_parts.append(f"\n## 用户当前请求\n{user_query}\n")
        prompt_parts.append("""## 输出要求
请基于以上所有信息，直接给出最终回答。
- 清晰、有条理
- 如果涉及课程，列出课程代码和名称
- 若信息不足，请明确说“根据当前课程库无法确认”
- 不要输出 Thought 或 Action，只输出最终答案

最终答案：""")

        return "\n".join(prompt_parts)
```

---

## 2️⃣ `src/prompt/parser.py`

```python
import re
from typing import Tuple, Optional

class ReActParser:
    @staticmethod
    def parse(response: str) -> Tuple[Optional[str], Optional[str]]:
        thought = None
        action = None

        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|$)", response, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        action_match = re.search(r"Action:\s*(.+)", response)
        if action_match:
            action = action_match.group(1).strip()

        return thought, action

    @staticmethod
    def parse_action(action_str: str) -> Tuple[str, dict]:
        pattern = r"(\w+)\((.*)\)"
        match = re.search(pattern, action_str)
        if not match:
            raise ValueError(f"Invalid action format: {action_str}")

        tool_name = match.group(1)
        args_str = match.group(2)

        kwargs = {}
        if args_str.strip():
            arg_pattern = r"(\w+)\s*=\s*(?P<quote>['\"]?)(.*?)(?P=quote)(?:,|$)"
            for m in re.finditer(arg_pattern, args_str):
                key = m.group(1)
                value = m.group(3).strip()
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                kwargs[key] = value
        return tool_name, kwargs
```

---

## 3️⃣ `src/prompt/client.py`

```python
import ollama
from typing import Optional

class OllamaClient:
    def __init__(self, model: str = "llama2:latest", temperature: float = 0.2):
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature},
            raw=True,
        )
        return response["response"]
```

---

## 4️⃣ `src/tools/tool_registry.py`（最小模拟版本）

```python
class ToolRegistry:
    def __init__(self):
        self._tools = {
            "rag_search": self._rag_search,
            "optimize_schedule": self._optimize_schedule,
            "generate_timetable": self._generate_timetable,
            "get_course_prerequisites": self._get_course_prerequisites,
            "check_semester_availability": self._check_semester_availability,
        }

    def execute(self, tool_name: str, **kwargs):
        if tool_name not in self._tools:
            return f"未知工具: {tool_name}"
        return self._tools[tool_name](**kwargs)

    def _rag_search(self, query: str, top_k: int = 5):
        # 模拟 RAG 返回
        return f"RAG检索结果：关于'{query}'，找到 {top_k} 条相关信息（模拟数据）"

    def _optimize_schedule(self, course_list: list, constraints: dict):
        return f"排课优化完成，课程 {course_list} 已按约束 {constraints} 安排"

    def _generate_timetable(self, courses: list, format: str = "weekly"):
        return f"已生成 {format} 课表，课程：{courses}，文件路径：/tmp/timetable.png"

    def _get_course_prerequisites(self, course_code: str):
        # 简单映射
        prereq_map = {
            "COMP7095": "COMP7105 Business Data Analytics",
            "COMP7125": "COMP7115 Programming Fundamentals",
        }
        return prereq_map.get(course_code, "无先修课程要求")

    def _check_semester_availability(self, course_code: str, semester: str):
        return f"{course_code} 在 {semester} 开设（模拟）"
```

---

## 5️⃣ `src/core/react_engine.py`

```python
import logging
from typing import List, Optional, Tuple

from src.prompt.builder import PromptBuilder, ConversationTurn
from src.prompt.parser import ReActParser
from src.prompt.client import OllamaClient
from src.tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class ReActEngine:
    def __init__(self,
                 llm_model: str = "llama2:latest",
                 max_iterations: int = 5,
                 temperature: float = 0.2):
        self.llm_client = OllamaClient(model=llm_model, temperature=temperature)
        self.parser = ReActParser()
        self.tool_registry = ToolRegistry()
        self.max_iterations = max_iterations
        self.history: List[ConversationTurn] = []

    def _plan_action(self,
                     user_query: str,
                     rag_context: Optional[str] = None,
                     recent_observations: Optional[List[str]] = None) -> Tuple[Optional[str], Optional[str]]:
        context = rag_context or ""
        if recent_observations:
            context += "\n\n## 最近的观察结果\n" + "\n".join(f"- {obs}" for obs in recent_observations[-3:])

        prompt = PromptBuilder.build(
            user_query=user_query,
            history=self.history,
            rag_context=context,
            max_history_turns=3
        )
        response = self.llm_client.generate(prompt)
        thought, action = self.parser.parse(response)
        return thought, action

    def _execute_action(self, action_str: str) -> str:
        try:
            tool_name, kwargs = self.parser.parse_action(action_str)
            result = self.tool_registry.execute(tool_name, **kwargs)
            return f"工具 {tool_name} 返回：{result}"
        except Exception as e:
            return f"工具执行错误：{str(e)}"

    def _generate_final_answer(self,
                               user_query: str,
                               rag_context: Optional[str] = None,
                               observations: Optional[List[str]] = None) -> str:
        prompt = PromptBuilder.build_final_answer_prompt(
            user_query=user_query,
            rag_context=rag_context,
            history=self.history,
            observations=observations
        )
        return self.llm_client.generate(prompt)

    def run(self,
            user_input: str,
            rag_context: Optional[str] = None,
            initial_observations: Optional[List[str]] = None) -> str:
        self.history.append(ConversationTurn(role="user", content=user_input))
        observations = initial_observations.copy() if initial_observations else []

        for iteration in range(self.max_iterations):
            thought, action = self._plan_action(
                user_query=user_input,
                rag_context=rag_context,
                recent_observations=observations
            )
            if not action:
                logger.warning("No action generated, stopping.")
                break

            if action.strip().lower().startswith("stop"):
                logger.info("Stop action received, finishing ReAct loop.")
                break

            observation = self._execute_action(action)
            observations.append(observation)

        final_answer = self._generate_final_answer(
            user_query=user_input,
            rag_context=rag_context,
            observations=observations
        )
        self.history.append(ConversationTurn(role="assistant", content=final_answer))
        return final_answer
```

---

## 6️⃣ `main.py` 测试入口

```python
#!/usr/bin/env python
import logging
from src.core.react_engine import ReActEngine

logging.basicConfig(level=logging.INFO)

def main():
    engine = ReActEngine(llm_model="llama2:latest", max_iterations=3, temperature=0.2)

    # 模拟 RAG 上下文（实际应由其他队员的 RAG 模块提供）
    rag_context = """根据课程库：
- COMP7095 Big Data Management 的先修课程是 COMP7105 Business Data Analytics
- COMP7095 开设于 Semester 2
- 该课程学分为 3 学分
"""

    user_query = "COMP7095 的先修课程是什么？"
    print(f"用户: {user_query}\n")
    answer = engine.run(user_input=user_query, rag_context=rag_context)
    print(f"助手: {answer}\n")

    # 第二个测试：需要调用工具
    user_query2 = "帮我排一下 COMP7095 和 COMP7125 的课表，每学期最多5门"
    print(f"用户: {user_query2}\n")
    answer2 = engine.run(user_input=user_query2, rag_context=rag_context)
    print(f"助手: {answer2}\n")

if __name__ == "__main__":
    main()
```

---

## ▶️ 运行方法

1. 确保已安装依赖：
   ```bash
   pip install ollama
   ```
2. 确保 Ollama 服务运行，并已拉取模型（例如 `llama2:latest`）：
   ```bash
   ollama pull llama2:latest
   ollama serve
   ```
3. 在项目根目录运行：
   ```bash
   python main.py
   ```

---

## ✅ 说明

- **Prompt 模块完全独立**，只负责构造字符串和解析响应，不依赖 RAG 或 ReAct 循环。
- **ReAct 引擎**调用 Prompt 模块，并通过工具注册表执行动作。
- **工具注册表**目前是模拟实现，实际项目中请替换为其他队员开发的真实工具（如调用 ChromaDB、排课算法等）。
- **RAG 上下文**通过 `rag_context` 参数传入，实际使用时由其他队员的 RAG 检索模块生成。