# 开发指南 (DEVELOPMENT.md)

## 项目开发流程和贡献指南

本文档描述如何在本项目上进行开发、测试和贡献。

---

## 📋 开发环境设置

### 1. 克隆项目

```bash
git clone <repository_url>
cd COMP7125-Group-Project
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # 如果使用pyproject.toml
```

### 4. 启动服务

```bash
# 终端1: 启动Ollama
ollama pull llama2:13b
ollama serve

# 终端2: 启动FastAPI
python -m uvicorn src.api.main:app --reload

# 终端3: 交互式演示
python example_usage.py
```

---

## 🏗️ 项目架构

### 核心模块

#### `src/core/react_engine.py` - ReAct核心引擎
- **Thought**: 思考步骤类
- **Action**: 行动步骤类
- **Observation**: 观察步骤类
- **ReActState**: 执行状态容器
- **ReActEngine**: 主引擎类

#### `src/tools/` - 工具集合
- `rag_tool.py`: RAG课程检索
- `schedule_optimizer.py`: 排课优化
- `visualization_tools.py`: 本地可视化
- `online_services.py`: 在线API集成
- `tool_registry.py`: 工具注册中心

#### `src/config/` - 配置管理
- `llm_config.py`: LLM配置 (Ollama等)
- `tools_config.py`: 工具参数配置

#### `src/utils/` - 工具函数
- `types.py`: 数据类型定义
- `data_parser.py`: 数据解析
- `validators.py`: 数据验证

#### `src/api/` - API接口
- `main.py`: FastAPI主应用
- `routes.py`: 路由定义
- `models.py`: Pydantic数据模型

---

## 🔨 开发任务清单

### Phase 2: ReAct核心引擎 (进行中)

**已完成:**
- [x] 数据模型定义 (Thought, Action, Observation, State)
- [x] ReActEngine 类框架
- [x] 基础的循环逻辑

**待做:**
- [ ] LLM集成 (_think 方法)
- [ ] Action规划逻辑 (_plan_action 方法)
- [ ] 工具调用执行 (_execute_action 方法)
- [ ] 错误处理和重试机制
- [ ] 执行状态持久化

**相关文件:**
- `src/core/react_engine.py`
- `tests/test_react_engine.py`

### Phase 3: 工具集实现 (待开始)

#### 任务3.1: RAG检索工具
**待做:**
- [ ] ChromaDB初始化
- [ ] 向量化查询
- [ ] 相似度搜索
- [ ] 结果解析

**文件:** `src/tools/rag_tool.py`

#### 任务3.2: 排课优化工具
**待做:**
- [ ] 冲突检测算法
- [ ] Greedy排课算法
- [ ] Hungarian匹配算法
- [ ] 约束条件处理

**文件:** `src/tools/schedule_optimizer.py`

#### 任务3.3: 可视化工具
**待做:**
- [ ] Matplotlib课表绘制
- [ ] Plotly统计图表
- [ ] Mermaid在线集成
- [ ] PNG/PDF导出

**文件:** 
- `src/tools/visualization_tools.py`
- `src/tools/online_services.py`

### Phase 4: LLM集成 (待开始)

**待做:**
- [ ] Ollama连接测试
- [ ] 提示词优化
- [ ] Tool calling格式
- [ ] 流式响应支持

**文件:** `src/config/llm_config.py`

### Phase 5: API开发 (待开始)

**待做:**
- [ ] POST /api/schedule/generate
- [ ] POST /api/schedule/validate
- [ ] GET /api/schedule/export/{file_id}
- [ ] POST /api/rag/search
- [ ] 错误处理中间件
- [ ] 请求日志记录

**文件:** `src/api/main.py`

---

## ✅ 测试和质量保证

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_react_engine.py -v

# 运行特定测试
pytest tests/test_react_engine.py::test_react_engine_init -v

# 运行带覆盖率
pytest tests/ --cov=src --cov-report=html
```

### 代码风格检查

```bash
# 使用Black格式化
black src/ tests/

# 使用Flake8检查
flake8 src/ tests/

# 使用mypy类型检查
mypy src/
```

### 性能测试

```bash
# 测试ReAct循环速度
python -m pytest tests/test_performance.py -v

# 测试排课算法 (100+课程)
python -m pytest tests/test_optimization.py::test_large_dataset -v
```

---

## 📝 编码规范

### Python风格

- 遵循 PEP 8 规范
- 使用 Black 自动格式化 (行宽 100)
- 使用 isort 管理导入
- 使用 type hints

### 推荐代码结构

```python
"""模块说明"""

from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DataModel:
    """数据模型说明"""
    field1: str
    field2: int = 0


class MainClass:
    """主类说明"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def public_method(self) -> Dict:
        """
        公开方法说明
        
        Args:
            param1: 参数说明
            
        Returns:
            返回值说明
        """
        pass
    
    def _private_method(self) -> None:
        """私有方法说明"""
        pass


def standalone_function(param: str) -> List[str]:
    """
    独立函数说明
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
        
    Example:
        >>> result = standalone_function("test")
        >>> print(result)
    """
    pass
```

### 文档字符串

- 所有公开函数/类必须有docstring
- 使用Google风格的docstring
- 包含 Args, Returns, Raises, Example

---

## 🔄 工作流程

### 1. 创建新功能

```bash
# 创建特性分支
git checkout -b feature/feature-name

# 开发并测试
# ...

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送分支
git push origin feature/feature-name
```

### 2. 提交Pull Request

- 编写清晰的PR描述
- 参考相关的issue
- 确保所有测试通过
- 等待代码审查

### 3. 代码审查

- 至少需要1个批准
- 所有CI检查必须通过
- 合并后删除分支

---

## 🐛 调试技巧

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 调试ReAct循环

```python
engine = ReActEngine()
engine.logger.setLevel(logging.DEBUG)
result = engine.run("user_query")

# 查看详细执行步骤
for i, thought in enumerate(result.thoughts):
    print(f"Thought {i}: {thought.content}")

for i, action in enumerate(result.actions):
    print(f"Action {i}: {action.to_json()}")

for i, obs in enumerate(result.observations):
    print(f"Observation {i}: {obs.result}")
```

### 联系LLM调试

```python
from src.config.llm_config import LLM_CONFIG
import requests

# 测试Ollama连接
response = requests.get(f"{LLM_CONFIG['base_url']}/api/tags")
print(response.json())
```

---

## 📚 资源和文档

### 内部文档
- [REACT_IMPLEMENTATION_PLAN.md](REACT_IMPLEMENTATION_PLAN.md) - 完整实现计划
- [README.md](README.md) - 项目概述

### 外部资源
- [LangChain文档](https://python.langchain.com/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Ollama文档](https://ollama.ai/)
- [ChromaDB文档](https://docs.trychroma.com/)

---

## 🤝 贡献指南

### 提交类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码风格 (无逻辑变化)
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 其他 (build, deps等)

### 提交信息格式

```
type(scope): subject

body (optional)

footer (optional)
```

示例:
```
feat(react-engine): add retry mechanism for tool execution

This adds exponential backoff retry logic to handle transient
tool execution failures.

Fixes #123
```

---

## 📊 项目进度

![Progress](https://img.shields.io/badge/Progress-30%25-blue)

- ✅ Phase 1: 环境配置 (0.5天)
- 🔄 Phase 2: ReAct核心 (2天) - 进行中
- ⏳ Phase 3: 工具集 (3天)
- ⏳ Phase 4: LLM集成 (1.5天)
- ⏳ Phase 5: API开发 (1.5天)
- ⏳ Phase 6: 测试 (2天)

---

## 📞 联系方式

- 项目Lead: [Name]
- 技术讨论: [Slack频道]
- Bug报告: [GitHub Issues]

---

**最后更新**: 2026-04-08  
**版本**: 1.0.0-beta
