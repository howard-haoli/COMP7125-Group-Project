# ReAct课程可视化系统 - 完整实现计划

**项目名称**: COMP7125-Group-Project  
**技术栈**: Python + FastAPI + Ollama + LangChain  
**创建日期**: 2026-04-08

---

## 📋 目录

- [1. 项目概述](#1-项目概述)
- [2. 系统架构](#2-系统架构)
- [3. 实现阶段](#3-实现阶段)
- [4. 工具定义与参数](#4-工具定义与参数)
- [5. 配置文件](#5-配置文件)
- [6. API设计](#6-api设计)
- [7. 验证测试](#7-验证测试)
- [8. 部署与优化](#8-部署与优化)

---

## 1. 项目概述

### 1.1 功能需求

构建一个基于**RAG + ReAct**的课程管理系统：

| 需求 | 描述 |
|------|------|
| **RAG检索** | 从课程文本库（PDF/Word）中检索课程信息 |
| **智能排课** | 自动检测时间冲突，进行排课优化 |
| **课表可视化** | 生成周课表页面（时间表格式） |
| **统计分析** | 生成饼图/柱状图等统计图表 |
| **Excel导出** | 导出含图表的结构化Excel文件 |
| **自然语言交互** | 用户通过自然语言问题触发完整的ReAct链 |

### 1.2 用户交互流程

```
用户: "给我生成本周课表，并统计每天的课程数量"
     ↓
[ReAct Engine 多轮推理]
  Thought 1 → Action 1 (retrieve_course_info) → Observation 1
  Thought 2 → Action 2 (optimize_schedule) → Observation 2
  Thought 3 → Actions 3-4 (generate visualizations) → Observations 3-4
  Thought 5 → Action 5 (STOP)
     ↓
系统: "✅ 课表已生成 + 统计图表已生成"
```

---

## 2. 系统架构

### 2.1 高层架构

```
Client/Frontend
    ↓
FastAPI Server (src/api/main.py)
    ↓
ReAct Engine Core (src/core/react_engine.py)
├─ Thought: LLM推理
├─ Action: 工具规划和调用
├─ Observation: 结果收集
└─ Loop: 迭代直到完成
    ↓
┌─────────┬───────────┬────────────┬──────────────┐
RAG Tool  Schedule   Visualization  Online
         Optimizer   Tools         Services
│        │           │             │
↓        ↓           ↓             ↓
ChromaDB Python    Matplotlib    Mermaid/
Ollama   Algorithms Plotly        Plotly API
```

### 2.2 项目文件结构

```
COMP7125-Group-Project/
├── REACT_IMPLEMENTATION_PLAN.md
├── requirements.txt
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── react_engine.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── rag_tool.py
│   │   ├── schedule_optimizer.py
│   │   ├── visualization_tools.py
│   │   ├── online_services.py
│   │   └── tool_registry.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── llm_config.py
│   │   └── tools_config.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_parser.py
│   │   ├── validators.py
│   │   └── types.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── models.py
│   └── rag/
│       ├── __init__.py
│       ├── vector_store.py
│       └── retrievers.py
│
├── data/
│   ├── chroma_db/
│   ├── sample_courses.pdf
│   └── output/
│
└── tests/
    ├── __init__.py
    ├── test_react_engine.py
    ├── test_tools.py
    └── test_api.py
```

---

## 3. 实现阶段

### Phase 1: 环境配置 (0.5天)
- 创建项目结构
- 安装依赖
- 启动Ollama + ChromaDB

### Phase 2: ReAct引擎 (2天)
- 定义数据模型（Thought, Action, Observation, State）
- 实现核心循环逻辑
- 工具注册机制

### Phase 3: 工具集实现 (3天)
- RAG课程检索工具
- 智能排课优化工具
- 本地/在线可视化工具

### Phase 4: LLM集成 (1.5天)
- Ollama连接
- 提示词设计和优化
- Tool calling格式

### Phase 5: API开发 (1.5天)
- FastAPI路由设计
- 请求/响应模型
- 错误处理

### Phase 6: 测试调试 (2天)
- 单元测试
- 集成测试
- 性能测试

---

## 4. 工具定义与参数

### 工具1：RAG课程检索 `retrieve_course_info`

**参数**:
```python
{
    "query": str,                 # 自然语言查询
    "semester": str = "current",  # 学期
    "department": str = None,     # 系别筛选
    "limit": int = 50             # 结果上限
}
```

**返回**:
```python
{
    "success": bool,
    "courses": List[Course],
    "total_count": int,
    "metadata": {...}
}
```

### 工具2：智能排课 `optimize_schedule`

**参数**:
```python
{
    "courses": List[Course],
    "constraints": {
        "no_conflicts": bool = True,
        "no_teacher_conflicts": bool = True,
        "continuous_hours": int = 4
    },
    "algorithm": str = "greedy"
}
```

**返回**:
```python
{
    "success": bool,
    "courses_optimized": List[Course],
    "conflicts_resolved": int,
    "summary": str
}
```

### 其他工具

| 工具名 | 功能 | 返回 |
|--------|------|------|
| **generate_timetable_local** | 本地生成课表 | file_path |
| **generate_timetable_mermaid** | Mermaid课表 | image_url, file_path |
| **generate_statistics_local** | 本地统计图 | file_path |
| **generate_statistics_plotly** | Plotly交互图 | image_url, file_path |
| **export_to_excel** | Excel导出 | file_path |

---

## 5. 配置文件

### 5.1 LLM配置 (src/config/llm_config.py)

```python
LLM_CONFIG = {
    "type": "ollama",
    "base_url": "http://localhost:11434",
    "model": "llama2:13b",
    "temperature": 0.7,
    "max_tokens": 2048,
    "react": {
        "max_iterations": 5,
        "stop_phrases": ["Final Answer:", "完成"]
    }
}
```

### 5.2 工具配置 (src/config/tools_config.py)

```python
TOOLS_CONFIG = {
    "rag": {
        "vector_db": "chromadb",
        "db_path": "./data/chroma_db",
        "model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "schedule_optimizer": {
        "algorithm": "greedy",
        "max_continuous_hours": 4
    },
    "visualization": {
        "local": {
            "matplotlib": {"dpi": 300, "figsize": (16, 9)}
        },
        "online": {
            "mermaid": {"api": "https://mermaid.ink/img/"}
        }
    }
}
```

---

## 6. API设计

### POST /api/schedule/generate

生成课表和统计图表

**请求**:
```json
{
    "user_query": "给我生成本周课表",
    "include_excel": true,
    "visualization_types": ["timetable", "statistics"]
}
```

**响应**:
```json
{
    "success": true,
    "react_steps": [...],
    "output_files": {
        "timetable": "/api/files/timetable.png",
        "statistics": ["/api/files/stats.png"]
    },
    "summary": "✅ 课表已生成"
}
```

### 其他端点

- `POST /api/schedule/validate` - 验证课程数据
- `GET /api/schedule/export/{file_id}` - 下载文件
- `POST /api/rag/search` - 搜索课程信息

---

## 7. 验证测试

### 单元测试
- RAG检索功能
- 排课冲突检测
- 可视化生成
- ReAct循环逻辑

### 集成测试
- 端到端用户请求
- 大规模数据处理（100+课程）
- API超时和错误处理

### 性能指标
- ReAct单循环: < 5秒
- 排课优化: < 2秒 (100门课)
- 图表生成: < 3秒

---

## 8. 部署与优化

### 生产部署

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app
```

### 优化建议

1. **缓存**: Redis缓存RAG查询结果
2. **异步**: Celery处理长时间任务
3. **向量索引**: FAISS替代ChromaDB线性搜索
4. **流式输出**: WebSocket实时推送

---

## 时间估计

| 阶段 | 工作量 |
|------|--------|
| 环境配置 | 0.5天 |
| ReAct引擎 | 2天 |
| 工具集 | 3天 |
| LLM集成 | 1.5天 |
| API开发 | 1.5天 |
| 测试 | 2天 |
| **总计** | **10.5天** |

---

## 关键依赖与工具选择

| 功能 | 方案 | 原因 |
|------|------|------|
| 课表生成 | Matplotlib + Mermaid | 灵活，支持多种格式 |
| 统计图表 | Plotly | 交互式，美观 |
| LLM推理 | Ollama + Llama2 | 完全免费，本地化 |
| 向量化 | SentenceTransformers | 轻量，无需API |
| 向量存储 | ChromaDB | 本地化，易部署 |
| 数据格式 | openpyxl | 标准Excel支持 |

---

**版本**: 1.0  
**最后更新**: 2026-04-08  
**项目团队**: COMP7125 Group
