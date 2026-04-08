# ReAct课程可视化系统 - COMP7125 Group Project

一个基于**RAG + ReAct**的智能课程管理和可视化系统。使用开源LLM (Ollama/Llama2)、ChromaDB和FastAPI构建。

## 🎯 项目特性

- ✅ **RAG课程检索**: 从文本库中检索课程信息
- ✅ **ReAct推理链**: 多轮思考-行动-观察循环
- ✅ **智能排课**: 自动检测和解决时间冲突
- ✅ **课表可视化**: 生成周课表图表
- ✅ **统计分析**: 生成各类统计图表
- ✅ **数据导出**: 支持Excel导出
- ✅ **自然语言交互**: 支持中英文混合查询

## 📁 项目结构

```
COMP7125-Group-Project/
├── REACT_IMPLEMENTATION_PLAN.md    # 详细实现计划文档
├── requirements.txt                 # Python依赖
├── README.md                         # 本文件
│
├── src/                              # 源代码目录
│   ├── core/                         # ReAct核心引擎
│   │   └── react_engine.py          # 思考-行动-观察循环
│   ├── tools/                        # 工具集合
│   │   ├── rag_tool.py              # RAG检索工具
│   │   ├── schedule_optimizer.py    # 排课优化工具
│   │   └── ...
│   ├── config/                       # 配置管理
│   │   ├── llm_config.py            # LLM配置
│   │   └── tools_config.py          # 工具配置
│   ├── utils/                        # 工具函数和类型
│   ├── api/                          # FastAPI接口
│   └── rag/                          # RAG系统
│
├── data/                             # 数据存储
│   ├── chroma_db/                   # ChromaDB向量库
│   └── output/                       # 输出文件目录
│
└── tests/                            # 测试目录
    └── test_react_engine.py         # 单元测试
```

## 🚀 快速开始

### 1. 克隆项目并安装依赖

```bash
cd COMP7125-Group-Project
pip install -r requirements.txt
```

### 2. 启动Ollama服务

```bash
# 安装Ollama (如果未安装)
# 访问: https://ollama.ai

# 下载模型
ollama pull llama2:13b

# 启动服务 (在新终端)
ollama serve
```

### 3. 启动FastAPI服务

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 测试API

```bash
# 生成课表
curl -X POST http://localhost:8000/api/schedule/generate \
  -H "Content-Type: application/json" \
  -d '{"user_query": "生成本周课表", "include_excel": true}'

# 健康检查
curl http://localhost:8000/health
```

## 📚 核心概念

### ReAct循环

```
用户输入: "给我生成本周课表，并统计每天的课程数量"
  ↓
[多轮迭代]
  Thought 1: "需要获取本周课程数据"
  Action 1: 调用 retrieve_course_info()
  Observation 1: 返回15门课程
  
  Thought 2: "检查是否有时间冲突"
  Action 2: 调用 optimize_schedule()
  Observation 2: 冲突已解决
  
  Thought 3: "生成可视化"
  Action 3-4: 调用生成工具
  Observation 3-4: 文件已生成
  
  Thought 5: "任务完成"
  Action 5: STOP
  ↓
输出: 课表图表 + 统计图 + Excel文件
```

## 🔧 配置

### LLM配置 (src/config/llm_config.py)

```python
LLM_CONFIG = {
    "type": "ollama",
    "base_url": "http://localhost:11434",
    "model": "llama2:13b",
    "temperature": 0.7,
    "react": {
        "max_iterations": 5
    }
}
```

### 工具配置 (src/config/tools_config.py)

```python
TOOLS_CONFIG = {
    "rag": {
        "vector_db": "chromadb",
        "db_path": "./data/chroma_db"
    },
    "schedule_optimizer": {
        "algorithm": "greedy"
    }
}
```

## 🧪 测试

运行单元测试：

```bash
pytest tests/ -v
```

## 📖 详细文档

完整的实现计划和API设计请查看：
- [REACT_IMPLEMENTATION_PLAN.md](REACT_IMPLEMENTATION_PLAN.md) - 详细实现计划

## 🤝 技术栈

| 组件 | 技术 | 原因 |
|------|------|------|
| LLM | Ollama + Llama2 | 完全开源，本地化 |
| 向量化 | SentenceTransformers | 轻量，无需API |
| 向量存储 | ChromaDB | 本地化，易部署 |
| Web框架 | FastAPI | 异步，高效能 |
| 可视化 | Matplotlib/Plotly | 灵活多样 |
| 数据处理 | Pandas/Numpy | 标准库 |

## 📊 性能目标

- ReAct单循环耗时: < 5秒
- 排课优化 (100门课): < 2秒
- 图表生成: < 3秒
- 内存占用: < 2GB

## 🔄 开发流程

### Phase 1: 环境配置 (0.5天) ✅
- 项目结构创建
- 依赖安装
- 配置文件设置

### Phase 2: ReAct核心 (2天) 🔄
- 数据模型定义
- 核心循环实现
- 工具注册机制

### Phase 3: 工具集实现 (3天) ⏳
- RAG工具开发
- 排课工具开发
- 可视化工具开发

### Phase 4: LLM集成 (1.5天) ⏳
- Ollama连接
- 提示词优化
- Tool calling实现

### Phase 5: API开发 (1.5天) ⏳
- 路由设计
- 数据模型
- 错误处理

### Phase 6: 测试调试 (2天) ⏳
- 单元测试
- 集成测试
- 性能优化

## 📝 API示例

### 生成课表

```bash
POST /api/schedule/generate

请求体:
{
    "user_query": "给我生成本周课表，并统计每天的课程数量",
    "include_excel": true,
    "visualization_types": ["timetable", "statistics"]
}

响应体:
{
    "success": true,
    "react_steps": [
        {
            "step": 1,
            "thought": "用户需要获取本周课程数据",
            "action": "retrieve_course_info",
            "observation": "返回15门课程"
        }
    ],
    "output_files": {
        "timetable": "/api/files/timetable.png",
        "statistics": ["/api/files/stats.png"],
        "excel": "/api/files/schedule.xlsx"
    },
    "summary": "✅ 课表已生成: 15门课程, 0个冲突"
}
```

## 🐛 常见问题

**Q: Ollama连接失败？**  
A: 确保Ollama服务运行在 http://localhost:11434

**Q: ChromaDB初始化错误？**  
A: 检查 `./data/chroma_db` 目录权限

**Q: 模型下载速度慢？**  
A: 可配置代理或使用国内镜像源

## 🚧 TODO

- [ ] 完整的RAG文本库加载
- [ ] LLM集成和提示词优化
- [ ] 完整的排课算法实现
- [ ] Matplotlib/Plotly集成
- [ ] Excel导出功能
- [ ] WebSocket实时推送
- [ ] 多用户支持和认证
- [ ] 数据库持久化

## 📄 许可

MIT License

## 👥 团队

COMP7125 Group Project Team

---

**更新时间**: 2026-04-08  
**版本**: 1.0.0-beta
