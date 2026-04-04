# 混合检索RAG系统执行计划

**项目名称**：基于RAG的学生问答系统（POC）  
**目标**：在1周内交付一个功能完整的混合检索问答系统  
**技术栈**：Python + LlamaIndex + 混合检索 + 三层分类架构  
**文档更新**：2026-04-04

---

## 目录

1. [项目概述](#项目概述)
2. [架构设计](#架构设计)
3. [混合检索机制](#混合检索机制)
4. [查询分类系统](#查询分类系统)
5. [权重配置方案](#权重配置方案)
6. [详细执行计划](#详细执行计划)
7. [代码框架](#代码框架)
8. [质量验证](#质量验证)
9. [部署与监控](#部署与监控)

---

## 项目概述

### 核心需求

- **处理数据**：49份课程PDF文档（COMP×14, GCAP×29, GFHC×6）
- **功能**：学生可通过自然语言查询文档，获得上下文相关答案
- **精度目标**：>85% 的用户问题得到准确回答
- **延迟目标**：单查询 < 2 秒
- **成本目标**：最小化API调用，优先离线可用

### 为什么选择混合检索？

| 问题 | 纯向量检索 | 混合检索 |
|------|----------|--------|
| 结构化数据精度 | 60-70% ❌ | 90-95% ✅ |
| 语义理解能力 | 85% ✅ | 88% ✅ |
| 幻觉风险 | 高 ❌ | 低 ✅ |
| 课程代码混淆 | 常见 ❌ | 罕见 ✅ |

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户查询                              │
│              "COMP7125的先修课程是什么?"                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │   第1层：查询分类器         │
        │  (规则 + 启发式)           │
        │  → STRUCTURED              │
        │  置信度: 0.9               │
        └────────────┬───────────────┘
                     │
      ┌──────────────┴──────────────┐
      │                             │
      ↓                             ↓
┌───────────────┐          ┌──────────────────┐
│ 关键词检索    │          │ 向量检索         │
│ (BM25)        │          │ (FAISS/Pinecone)│
│ Top-5结果     │          │ Top-5结果        │
└───────┬───────┘          └────────┬─────────┘
        │                          │
        │      权重配置            │
        │ keyword: 0.8  vector: 0.2│
        │                          │
        └──────────────┬───────────┘
                       │
                       ↓
            ┌──────────────────────┐
            │ 融合引擎            │
            │ • 倒数排序融合       │
            │ • 去重               │
            │ • 重新排序           │
            └──────────┬───────────┘
                       │
                       ↓
            ┌──────────────────────┐
            │ LLM生成答案         │
            │ + 来源引用          │
            │ + 置信度评分        │
            └──────────────────────┘
```

### 三层分类架构

```
┌─────────────────────────────────────┐
│  第1层：规则/启发式（快速路径）     │
├─────────────────────────────────────┤
│ 成功率: 60-75%                      │
│ 延迟: <100ms                        │
│ 成本: $0                            │
│ 使用: 正则表达式、关键词匹配        │
│ 触发: 70%的查询                     │
└─────────────────────────────────────┘
                   ↓ 
          (置信度<0.85时)
                   ↓
┌─────────────────────────────────────┐
│  第2层：轻量级NLP模型（精准路径）   │
├─────────────────────────────────────┤
│ 成功率: 80-90%                      │
│ 延迟: 100-500ms                     │
│ 成本: 极低（本地运行）             │
│ 使用: DistilBERT/TinyBERT          │
│ 触发: 25%的查询                     │
└─────────────────────────────────────┘
                   ↓
          (置信度<0.75时)
                   ↓
┌─────────────────────────────────────┐
│  第3层：大模型/人工审核（兜底）     │
├─────────────────────────────────────┤
│ 成功率: 95%+                        │
│ 延迟: >1000ms                       │
│ 成本: $0.0001-0.001/次             │
│ 使用: OpenAI API/人工               │
│ 触发: 5%的查询（例外情况）         │
└─────────────────────────────────────┘
```

---

## 混合检索机制

### 1. 关键词检索（BM25算法）

**适用于**：结构化数据、精确匹配、课程代码等

```python
# 特点：精确但无语义理解
输入查询: "COMP7125的先修?"
↓
提取关键词: ["COMP7125", "先修"]
↓
BM25匹配所有包含这些词的文档段落
↓
返回精确匹配结果
```

**优点**：
- 精确匹配课程代码（COMP7125 != COMP7124）
- 找到学分、先修等关键属性
- 速度快（毫秒级）
- 无需GPU

**缺点**：
- 无法理解语义相似性
- 处理同义词困难
- 不能发现隐含关系

### 2. 向量检索（语义搜索）

**适用于**：概念解释、语义相似、隐含含义等

```python
# 特点：理解语义但可能幻觉
输入查询: "解释设计在模式中的角色"
↓
转换为嵌入向量（语义空间）
↓
在向量空间中查找相似向量
↓
返回语义相关结果
```

**优点**：
- 理解深层语义
- 发现潜在相关信息
- 处理同义表述
- 理解抽象概念

**缺点**：
- 数值精度问题（学分3 vs 4）
- 可能返回相似但错误的结果
- 计算资源占用

### 3. 融合策略（倒数排序融合）

```
关键词搜索结果排序：
[文档1, 文档2, 文档3, 文档4, 文档5]
得分:  1.0   0.5    0.33   0.25   0.2

向量搜索结果排序：
[文档A, 文档2, 文档B, 文档3, 文档C]
得分:  1.0   0.5    0.33   0.25   0.2

权重应用（keyword=0.8, vector=0.2）：
───────────────────────────────────

对于重复出现的文档（文档2）：
关键词贡献: 0.5 × 0.8 = 0.40
向量贡献:   0.5 × 0.2 = 0.10
融合分数:   0.40 + 0.10 = 0.50 ✓（多源验证增加置信度）

对于仅在关键词出现的（文档1）：
融合分数: 1.0 × 0.8 = 0.80 ✓（精确匹配）

对于仅在向量出现的（文档A）：
融合分数: 1.0 × 0.2 = 0.20 ✗（权重低）

最终排序：
[文档1(0.80), 文档2(0.50), 文档3(0.33×0.2=0.067), ...]
```

---

## 查询分类系统

### 分类层次：三层架构

#### 第1层：规则分类

```python
# 判断条件
查询特征            → 分类结果
───────────────────────────────
包含COMP/GCAP/GFHC代码   → 倾向STRUCTURED
包含"学分/先修/小时"      → 倾向STRUCTURED
包含"是什么/解释/定义"    → 倾向SEMANTIC
包含"多少/几个/数量"      → 倾向STRUCTURED
包含"概念/原理/工作流程"  → 倾向SEMANTIC

规则命中>0 && 置信度>0.85 → 使用本规则结果
否则 → 进入第2层
```

**代码示例**：

```python
def classify_with_rules(query):
    structured_indicators = 0
    semantic_indicators = 0
    
    if re.search(r'(COMP|GCAP|GFHC)\d{4}', query):
        structured_indicators += 1
    if re.search(r'(学分|先修|小时|GPA)', query):
        structured_indicators += 1
    if re.search(r'(是什么|解释|定义|如何)', query):
        semantic_indicators += 1
    if re.search(r'(概念|原理|机制)', query):
        semantic_indicators += 1
    
    if structured_indicators > semantic_indicators:
        return "STRUCTURED", structured_indicators/2
    elif semantic_indicators > structured_indicators:
        return "SEMANTIC", semantic_indicators/2
    else:
        return "HYBRID", 0.5
```

#### 第2层：轻量级模型分类

```python
# 当规则置信度<0.85时触发
使用模型: DistilBERT (轻量级，<100MB)
输入: 原始查询文本
输出: 分类标签 + 置信度

置信度>0.75 → 使用模型结果
否则 → 进入第3层
```

#### 第3层：大模型/人工审核

```python
# 当模型置信度<0.75时触发（<5%查询）
选项A: 调用OpenAI API
  消息: "请分类此查询..."
  返回: 确定的分类

选项B: 人工审核队列
  标记为"需要审核"
  由人工标注
  学习反馈优化前两层
```

### 不同查询类型的处理

| 查询类型 | 示例 | 分类结果 | 权重配置 | 处理策略 |
|---------|------|---------|---------|---------|
| 结构化 | "COMP7125的学分?" | STRUCTURED | keyword:0.8, vector:0.2 | BM25优先 |
| 语义 | "什么是设计模式?" | SEMANTIC | keyword:0.2, vector:0.8 | 向量优先 |
| 混合 | "COMP7125用什么设计模式?" | HYBRID | keyword:0.5, vector:0.5 | 均衡融合 |
| 不确定 | "嗯...怎么说呢?" | HYBRID | keyword:0.5, vector:0.5 | 降级到混合 |

---

## 权重配置方案

### 基础权重（按查询类型）

```yaml
# config.yaml - 权重配置文件

weights:
  STRUCTURED:
    default:
      keyword: 0.8      # 关键词权重高
      vector: 0.2
    high_precision:     # 多个数值需求
      keyword: 0.9
      vector: 0.1
    
  SEMANTIC:
    default:
      keyword: 0.2
      vector: 0.8       # 向量权重高
    
  HYBRID:
    default:
      keyword: 0.5
      vector: 0.5       # 均衡

# 动态调整规则
adjustments:
  multiple_entities:
    delta: +0.05        # 多个课程代码 → keyword +0.05
    trigger: "多于1个课程代码"
  
  fuzzy_language:
    delta: +0.1         # 模糊语言 → vector +0.1
    trigger: "包含大概/差不多/左右"
  
  query_length:
    delta: +0.05        # 长查询 → vector +0.05
    trigger: "查询长度>30字符"
  
  numerical_precision:
    delta: +0.1         # 数值精度 → keyword +0.1
    trigger: "包含数值且问多少/几个"
```

### 权重计算流程

```
┌─────────────────────────────┐
│ 用户查询分类                 │
│ 得到: STRUCTURED             │
└────────────────┬─────────────┘
                 │
                 ↓
┌──────────────────────────────────┐
│ 选择基础权重                      │
│ keyword: 0.8, vector: 0.2        │
└────────────────┬─────────────────┘
                 │
                 ↓
┌──────────────────────────────────┐
│ 检查是否触发调整规则              │
│ • 包含数值? +0.1 keyword          │
│ • 多个代码? +0.05 keyword         │
│ • 模糊语言? +0.1 vector           │
│ • 长查询? +0.05 vector            │
└────────────────┬─────────────────┘
                 │
                 ↓
┌──────────────────────────────────┐
│ 应用调整后重新归一化              │
│ 确保 keyword + vector = 1.0      │
│ 最终: keyword: 0.878, vector: 0.122
└──────────────────────────────────┘
```

### 权重对检索的影响

```python
# 示例：某文档在关键词排名1，向量排名5

关键词分数: 1.0 / 1 = 1.0
向量分数:   1.0 / 5 = 0.2

不同权重配置下的最终分数:
────────────────────────────────
keyword=0.9, vector=0.1:
  最终分数 = 1.0×0.9 + 0.2×0.1 = 0.92  ✓✓ 极度倾向关键词

keyword=0.8, vector=0.2:
  最终分数 = 1.0×0.8 + 0.2×0.2 = 0.84  ✓ 明显倾向关键词

keyword=0.5, vector=0.5:
  最终分数 = 1.0×0.5 + 0.2×0.5 = 0.60  ← 均衡

keyword=0.2, vector=0.8:
  最终分数 = 1.0×0.2 + 0.2×0.8 = 0.36  ✗ 倾向向量

keyword=0.1, vector=0.9:
  最终分数 = 1.0×0.1 + 0.2×0.9 = 0.28  ✗✗ 极度倾向向量
```

---

## 详细执行计划

### 第1周：POC交付

#### 第1-2天：环境与数据准备

**Day 1：环境搭建**

```bash
# 1. 创建项目结构
project/
├── config/
│   ├── config.yaml              # 权重配置
│   └── .env                     # 环境变量
├── src/
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   ├── document_manager.py      # PDF处理
│   ├── query_classifier.py      # 查询分类
│   ├── retriever.py            # 混合检索
│   ├── rag_engine.py           # RAG核心
│   └── api.py                  # REST API
├── data/
│   ├── raw/                    # 原始PDF（resource/文件夹）
│   └── processed/              # 处理后的向量索引
├── tests/
│   ├── test_classifier.py
│   ├── test_retriever.py
│   └── test_integration.py
├── requirements.txt
└── README.md

# 2. Python虚拟环境
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

**requirements.txt**：
```
llama-index==0.9.0
pypdf==3.16.0
openai==0.28.0
pydantic==2.0.0
fastapi==0.104.0
uvicorn==0.24.0
python-dotenv==1.0.0
rank-bm25==0.2.2
faiss-cpu==1.7.4
numpy==1.24.0
```

**Day 2：数据预处理**

```python
# src/document_manager.py 核心代码

class DocumentManager:
    def __init__(self, pdf_directory: str):
        self.pdf_directory = pdf_directory
        self.documents = []
        self.nodes = []
    
    def load_documents(self):
        """加载所有PDF文档"""
        from llama_index import SimpleDirectoryReader
        
        reader = SimpleDirectoryReader(self.pdf_directory)
        self.documents = reader.load_data()
        
        # 添加元数据标记
        for doc in self.documents:
            # 提取课程类别
            if 'COMP' in doc.metadata.get('file_name', ''):
                doc.metadata['category'] = 'COMP'
            elif 'GCAP' in doc.metadata.get('file_name', ''):
                doc.metadata['category'] = 'GCAP'
            elif 'GFHC' in doc.metadata.get('file_name', ''):
                doc.metadata['category'] = 'GFHC'
        
        print(f"✓ 加载{len(self.documents)}份文档")
        return self.documents
    
    def chunk_documents(self, chunk_size: int = 512):
        """分块处理文档"""
        from llama_index.node_parser import SimpleNodeParser
        
        parser = SimpleNodeParser.from_defaults(
            chunk_size=chunk_size,
            chunk_overlap=50  # 块重叠以保持连贯性
        )
        
        self.nodes = parser.get_nodes_from_documents(self.documents)
        print(f"✓ 分块后得到{len(self.nodes)}个文档段落")
        return self.nodes

# 使用
doc_manager = DocumentManager('resource/')
doc_manager.load_documents()
doc_manager.chunk_documents()
```

---

#### 第3-4天：混合检索核心构建

**Day 3：索引和检索器构建**

```python
# src/retriever.py 核心代码

from llama_index import VectorStoreIndex
from llama_index.retrievers import VectorIndexRetriever, BM25Retriever
from rank_bm25 import BM25Okapi
from collections import defaultdict
import numpy as np

class HybridRetriever:
    def __init__(self, nodes, use_faiss=True):
        self.nodes = nodes
        
        # 初始化向量索引
        if use_faiss:
            from llama_index.vector_stores import FAISSVectorStore
            from llama_index import VectorStoreIndex
            
            vector_store = FAISSVectorStore()
            self.vector_index = VectorStoreIndex(
                nodes,
                vector_store=vector_store
            )
        
        # 初始化BM25检索器
        corpus = [node.get_content() for node in nodes]
        self.bm25 = BM25Okapi(corpus)
        
        print("✓ 混合检索器初始化完成")
    
    def retrieve_hybrid(self, 
                        query: str, 
                        top_k: int = 5,
                        weights: dict = None):
        """
        执行混合检索
        
        Args:
            query: 用户查询
            top_k: 返回结果数量
            weights: {'keyword': 0.8, 'vector': 0.2}
        
        Returns:
            融合后的结果列表
        """
        
        if weights is None:
            weights = {'keyword': 0.8, 'vector': 0.2}
        
        # 第1步：关键词检索
        keyword_results = self._bm25_search(query, top_k)
        
        # 第2步：向量检索
        vector_results = self._vector_search(query, top_k)
        
        # 第3步：融合
        merged = self._merge_results(
            keyword_results, 
            vector_results,
            weights
        )
        
        return merged
    
    def _bm25_search(self, query: str, top_k: int):
        """BM25关键词搜索"""
        scores = self.bm25.get_scores(query.split())
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = [
            {
                'node_id': self.nodes[i].node_id,
                'content': self.nodes[i].get_content(),
                'score': scores[i],
                'rank': idx
            }
            for idx, i in enumerate(top_indices)
        ]
        
        return results
    
    def _vector_search(self, query: str, top_k: int):
        """向量语义搜索"""
        from llama_index.retrievers import VectorIndexRetriever
        
        retriever = VectorIndexRetriever(
            index=self.vector_index,
            similarity_top_k=top_k
        )
        
        nodes = retriever.retrieve(query)
        
        results = [
            {
                'node_id': node.node_id,
                'content': node.get_content(),
                'score': node.score or 0.5,
                'rank': idx
            }
            for idx, node in enumerate(nodes)
        ]
        
        return results
    
    def _merge_results(self, keyword_results, vector_results, weights):
        """倒数排序融合"""
        fusion_scores = defaultdict(float)
        node_map = {}
        
        # 关键词结果加权
        for item in keyword_results:
            score = 1.0 / (item['rank'] + 1)
            weighted_score = score * weights['keyword']
            fusion_scores[item['node_id']] += weighted_score
            node_map[item['node_id']] = item
        
        # 向量结果加权
        for item in vector_results:
            score = 1.0 / (item['rank'] + 1)
            weighted_score = score * weights['vector']
            fusion_scores[item['node_id']] += weighted_score
            if item['node_id'] not in node_map:
                node_map[item['node_id']] = item
        
        # 按融合分数排序
        sorted_results = sorted(
            fusion_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [node_map[nid] for nid, _ in sorted_results]

# 使用
retriever = HybridRetriever(nodes)
results = retriever.retrieve_hybrid(
    "COMP7125的先修课程是什么?",
    top_k=5,
    weights={'keyword': 0.8, 'vector': 0.2}
)
```

**Day 4：查询分类器构建**

```python
# src/query_classifier.py 核心代码

import re
from enum import Enum

class QueryType(Enum):
    STRUCTURED = "structured"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

class QueryClassifier:
    def __init__(self):
        self.structured_patterns = {
            'course_code': r'\b(COMP|GCAP|GFHC)\d{4}\b',
            'attributes': r'(学分|小时|学时|分数|GPA|先修|前置)',
            'numbers': r'(多少|几个|多久)',
        }
        
        self.semantic_patterns = {
            'explain': r'(解释|说明|什么是|定义|如何)',
            'concept': r'(概念|原理|机制|工作原理)',
        }
    
    def classify(self, query: str) -> tuple[QueryType, float, dict]:
        """
        分类查询
        
        Returns:
            (QueryType, confidence, metadata)
        """
        
        # 计算匹配得分
        structured_hits = sum(
            1 for pattern in self.structured_patterns.values()
            if re.search(pattern, query, re.IGNORECASE)
        )
        
        semantic_hits = sum(
            1 for pattern in self.semantic_patterns.values()
            if re.search(pattern, query, re.IGNORECASE)
        )
        
        # 计算置信度
        total_patterns = len(self.structured_patterns) + len(self.semantic_patterns)
        structured_confidence = structured_hits / total_patterns
        semantic_confidence = semantic_hits / total_patterns
        
        # 判断分类
        if structured_confidence > semantic_confidence and structured_hits > 0:
            query_type = QueryType.STRUCTURED
            confidence = structured_confidence
        elif semantic_confidence > structured_confidence and semantic_hits > 0:
            query_type = QueryType.SEMANTIC
            confidence = semantic_confidence
        else:
            query_type = QueryType.HYBRID
            confidence = max(structured_confidence, semantic_confidence)
        
        metadata = {
            'structured_hits': structured_hits,
            'semantic_hits': semantic_hits,
            'query_length': len(query),
            'has_course_code': bool(re.search(r'(COMP|GCAP|GFHC)\d{4}', query)),
        }
        
        return query_type, confidence, metadata

# 使用
classifier = QueryClassifier()

test_queries = [
    "COMP7125的学分是多少?",
    "什么是设计模式?",
    "COMP7125涉及哪些设计原理?",
]

for q in test_queries:
    query_type, confidence, meta = classifier.classify(q)
    print(f"查询: {q}")
    print(f"  类型: {query_type.value}, 置信度: {confidence:.2f}")
    print(f"  元数据: {meta}\n")
```

---

#### 第5天：API与集成

**Day 5：REST API构建**

```python
# src/api.py 核心代码

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json

app = FastAPI(title="学生问答RAG系统")

# 数据模型
class QueryRequest(BaseModel):
    question: str
    course_filter: Optional[str] = None  # COMP/GCAP/GFHC
    top_k: int = 5

class SearchResult(BaseModel):
    content: str
    source: str
    category: str
    relevance_score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SearchResult]
    query_type: str
    confidence: float
    processing_time_ms: float

# 初始化
rag_engine = None

@app.on_event("startup")
async def startup():
    """应用启动时初始化RAG引擎"""
    global rag_engine
    from src.rag_engine import RAGEngine
    
    rag_engine = RAGEngine(
        pdf_directory="resource/",
        config_path="config/config.yaml"
    )
    print("✓ RAG引擎初始化完成")

@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """处理用户查询"""
    import time
    
    start_time = time.time()
    
    try:
        # 执行查询
        response = rag_engine.query(
            question=request.question,
            course_filter=request.course_filter,
            top_k=request.top_k
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            answer=response['answer'],
            sources=[
                SearchResult(
                    content=src['content'][:200],  # 截断显示
                    source=src['source'],
                    category=src['category'],
                    relevance_score=src['score']
                )
                for src in response['sources']
            ],
            query_type=response['query_type'],
            confidence=response['confidence'],
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# 启动: uvicorn src.api:app --reload --port 8000
```

---

#### 第6-7天：优化与部署

**Day 6：性能优化与测试**

```python
# src/rag_engine.py - 核心RAG引擎

import yaml
from typing import Optional, Dict, Any
from src.query_classifier import QueryClassifier
from src.retriever import HybridRetriever

class RAGEngine:
    def __init__(self, pdf_directory: str, config_path: str):
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化组件
        self.classifier = QueryClassifier()
        
        # 初始化检索器
        from src.document_manager import DocumentManager
        doc_manager = DocumentManager(pdf_directory)
        doc_manager.load_documents()
        nodes = doc_manager.chunk_documents()
        
        self.retriever = HybridRetriever(nodes)
        
        # 初始化LLM
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        self.llm_model = "gpt-3.5-turbo"
    
    def query(self, 
              question: str,
              course_filter: Optional[str] = None,
              top_k: int = 5) -> Dict[str, Any]:
        """
        主查询入口
        """
        
        # 第1步：查询分类
        query_type, confidence, meta = self.classifier.classify(question)
        
        print(f"\n[分类] {query_type.value} (置信度: {confidence:.2f})")
        
        # 第2步：选择权重
        weights = self._get_weights(query_type, meta)
        print(f"[权重] keyword={weights['keyword']:.2f}, vector={weights['vector']:.2f}")
        
        # 第3步：执行混合检索
        search_results = self.retriever.retrieve_hybrid(
            question,
            top_k=top_k,
            weights=weights
        )
        
        # 第4步：过滤课程类别（如果指定）
        if course_filter:
            # 过滤逻辑...
            pass
        
        # 第5步：生成答案
        answer = self._generate_answer(question, search_results)
        
        return {
            'answer': answer,
            'sources': search_results,
            'query_type': query_type.value,
            'confidence': confidence
        }
    
    def _get_weights(self, query_type, meta) -> Dict[str, float]:
        """根据查询特征获取最终权重"""
        
        # 从配置获取基础权重
        base_weights = self.config['weights'][query_type.value]['default'].copy()
        
        # 应用动态调整
        if meta['has_course_code'] and meta['query_length'] > 20:
            # 多个实体 → keyword +0.05
            adjustment = self.config['adjustments']['multiple_entities']['delta']
            base_weights['keyword'] += adjustment
            base_weights['vector'] -= adjustment
        
        # 归一化
        total = base_weights['keyword'] + base_weights['vector']
        base_weights['keyword'] /= total
        base_weights['vector'] /= total
        
        return base_weights
    
    def _generate_answer(self, question: str, search_results: list) -> str:
        """使用LLM生成答案"""
        
        # 构建上下文
        context = "\n".join([
            f"[来源{i+1}] {result['content']}"
            for i, result in enumerate(search_results[:3])
        ])
        
        # 构建提示词
        prompt = f"""基于以下上下文回答问题。如果上下文中没有答案，请说"我在文档中找不到相关信息"。

【上下文】
{context}

【问题】
{question}

【回答】"""
        
        import openai
        
        response = openai.ChatCompletion.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "你是一个有帮助的课程助手。基于提供的文档内容回答学生的问题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=512
        )
        
        return response['choices'][0]['message']['content']
```

**Day 7：部署与文档**

```bash
# 1. Docker化
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=your_key_here

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]

# 2. 启动脚本
# run.sh
python -m uvicorn src.api:app --reload --port 8000

# 3. 部署
docker build -t rag-qa-system .
docker run -p 8000:8000 -e OPENAI_API_KEY=xxxx rag-qa-system
```

---

## 代码框架

### 项目结构完整示例

```
rag-qa-system/
├── config/
│   ├── config.yaml              # 权重和配置
│   ├── prompts.yaml             # 提示词模板
│   └── .env.example
├── src/
│   ├── __init__.py
│   ├── config.py               # 配置加载
│   ├── document_manager.py      # PDF处理：加载+分块
│   ├── query_classifier.py      # 三层查询分类
│   ├── retriever.py            # 混合检索：BM25+向量+融合
│   ├── rag_engine.py           # RAG引擎：编排所有组件
│   ├── api.py                  # FastAPI REST接口
│   └── utils.py                # 工具函数
├── tests/
│   ├── test_classifier.py
│   ├── test_retriever.py
│   ├── test_rag_engine.py
│   └── test_integration.py
├── notebooks/
│   └── exploration.ipynb        # 数据探索
├── data/
│   ├── raw/                    # 原始PDF（指向resource/）
│   └── processed/              # 处理后的索引
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── run.sh
├── README.md
└── RAG_EXECUTION_PLAN.md        # 本文档
```

### 核心函数签名

```python
# 文档管理
class DocumentManager:
    def load_documents(self) -> List[Document]
    def chunk_documents(self, chunk_size: int) -> List[Node]

# 查询分类
class QueryClassifier:
    def classify(self, query: str) -> Tuple[QueryType, float, Dict]

# 混合检索
class HybridRetriever:
    def retrieve_hybrid(self, query: str, top_k: int, weights: Dict) -> List[Dict]
    def _bm25_search(self, query: str, top_k: int) -> List[Dict]
    def _vector_search(self, query: str, top_k: int) -> List[Dict]
    def _merge_results(self, keyword_results, vector_results, weights) -> List[Dict]

# RAG引擎
class RAGEngine:
    def query(self, question: str, course_filter: Optional[str], top_k: int) -> Dict
    def _get_weights(self, query_type, meta) -> Dict
    def _generate_answer(self, question: str, search_results: list) -> str

# API
@app.post("/api/query") -> QueryResponse
@app.get("/health") -> Dict
```

---

## 质量验证

### 验证清单

#### 功能验证

- [ ] **数据加载**
  - 所有49份PDF成功加载
  - 元数据正确标记（COMP/GCAP/GFHC）
  - 文本分块的连贯性完好

- [ ] **查询分类**
  - 规则层：80%+ 查询正确分类
  - 模型层：90%+ 查询正确分类
  - 综合准确率 > 85%

- [ ] **混合检索**
  - 关键词检索：课程代码精确匹配 100%
  - 向量检索：语义相似结果 > 80%
  - 融合结果：相关性前5名中有目标 > 90%

- [ ] **RAG生成**
  - 答案包含原文引用 100%
  - 答案的准确性 > 85%（人工评估）
  - 答案长度适中（100-500字）

- [ ] **API端点**
  - `/api/query` 响应正常
  - `/health` 健康检查工作
  - 错误处理完善

#### 性能验证

| 指标 | 目标 | 实际 |
|------|------|------|
| 单查询延迟 | <2s | |
| 吞吐量（并发5） | >5 req/s | |
| 向量索引大小 | <100MB | |
| 内存占用 | <2GB | |

#### 测试用例

```python
# tests/test_integration.py

TEST_QUERIES = [
    {
        'query': 'COMP7125的先修课程是什么?',
        'expected_category': 'STRUCTURED',
        'expected_answer_contains': ['COMP7115', '先修'],
    },
    {
        'query': '什么是设计模式?',
        'expected_category': 'SEMANTIC',
        'expected_answer_contains': ['设计', '模式'],
    },
    {
        'query': 'GCAP3005涉及哪些伦理学原理?',
        'expected_category': 'HYBRID',
        'expected_answer_contains': ['GCAP3005', '伦理'],
    },
]

def test_full_pipeline():
    engine = RAGEngine('resource/', 'config/config.yaml')
    
    for test_case in TEST_QUERIES:
        response = engine.query(test_case['query'])
        
        assert response['query_type'] == test_case['expected_category']
        assert response['confidence'] > 0.7
        
        for keyword in test_case['expected_answer_contains']:
            assert keyword in response['answer'], \
                f"答案中缺少'{keyword}': {response['answer']}"
```

---

## 部署与监控

### 本地部署

```bash
# 1. 克隆/进入项目
cd d:\Microsoft\ VS\ Code\COMP7125-Group-Project

# 2. 创建虚拟环境
python -m venv venv
source venv/Scripts/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
copy config/.env.example config/.env
# 编辑 config/.env，填入 OPENAI_API_KEY

# 5. 启动服务
python -m uvicorn src.api:app --reload --port 8000

# 6. 测试
curl "http://localhost:8000/health"
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "COMP7125的学分是多少?"}'
```

### 监控与日志

```python
# src/monitoring.py

import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rag_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class QueryMetrics:
    """查询性能统计"""
    
    def __init__(self):
        self.total_queries = 0
        self.successful_queries = 0
        self.avg_latency_ms = 0
        self.errors = 0
    
    def log_query(self, query_type, latency_ms, success=True):
        self.total_queries += 1
        
        if success:
            self.successful_queries += 1
        else:
            self.errors += 1
        
        self.avg_latency_ms = (
            (self.avg_latency_ms * (self.total_queries - 1) + latency_ms)
            / self.total_queries
        )
        
        logger.info(f"Query: type={query_type}, latency={latency_ms}ms, "
                   f"success={success}")
    
    def report(self):
        """生成统计报告"""
        success_rate = (self.successful_queries / self.total_queries * 100) \
                      if self.total_queries > 0 else 0
        
        report = f"""
        【系统统计】
        总查询数: {self.total_queries}
        成功率: {success_rate:.2f}%
        平均延迟: {self.avg_latency_ms:.2f}ms
        错误数: {self.errors}
        """
        
        logger.info(report)
        return report
```

### 常见故障排查

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| PDF加载失败 | 文件格式不支持 | 检查PDF是否损坏，尝试重新转换 |
| 检索无结果 | 向量索引未建立 | 确保运行 `document_manager.chunk_documents()` |
| 答案准确度低 | 权重配置不当 | 调整 `config.yaml` 中的权重值 |
| 延迟过高 | 向量搜索瓶颈 | 减少top_k或使用GPU加速 |
| API超时 | LLM API响应慢 | 增加超时时间或使用本地LLM |

---

## 附录

### 配置文件示例

**config.yaml**：
```yaml
# src/config.yaml

# 权重配置
weights:
  STRUCTURED:
    default:
      keyword: 0.8
      vector: 0.2
  SEMANTIC:
    default:
      keyword: 0.2
      vector: 0.8
  HYBRID:
    default:
      keyword: 0.5
      vector: 0.5

# 调整规则
adjustments:
  multiple_entities:
    delta: 0.05
  fuzzy_language:
    delta: 0.1
  query_length:
    delta: 0.05
    threshold: 30
  numerical_precision:
    delta: 0.1

# 检索配置
retrieval:
  top_k: 5
  chunk_size: 512
  chunk_overlap: 50

# LLM配置
llm:
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 512

# 向量数据库配置
vector_db:
  type: "faiss"  # 或 "pinecone"
  # pinecone_index: "rag-index"
  # pinecone_api_key: "${PINECONE_API_KEY}"
```

### 快速参考：权重建议

```
场景                          权重配置          说明
─────────────────────────────────────────────────────
学生查问课程属性              keyword:0.9       精确数值
(如"学分多少")               vector:0.1

理论概念解释                  keyword:0.2       语义理解
(如"什么是XXX")              vector:0.8

混合类问题                    keyword:0.5       均衡
(如"COMP7125用什么设计")    vector:0.5

不确定/模糊查询               keyword:0.5       保险方案
                            vector:0.5
```

### 性能基准

```
系统规模: 49份PDF, 分块后≈1000个nodes

关键词搜索 (BM25):
  初始化时间: <100ms
  查询时间: 5-50ms
  内存占用: <50MB

向量搜索 (FAISS):
  初始化时间: 2-5秒
  查询时间: 100-300ms
  内存占用: 200-500MB

融合 + LLM:
  融合时间: <50ms
  LLM生成时间: 1-3秒
  端到端延迟: 1.5-3.5秒

整体系统:
  日均处理能力: >10,000查询
  成本: <$1 (若仅用本地模型)
```

---

## 后续优化方向（第2-4周）

### Week 2: 精度优化
- [ ] 收集用户反馈，识别错误模式
- [ ] 微调权重配置
- [ ] 升级到混合模型分类（第2层）

### Week 3: 扩展功能
- [ ] 添加多语言支持
- [ ] 实现用户反馈学习循环
- [ ] 构建独立的结构化数据索引

### Week 4+: 生产级功能
- [ ] 用户认证与权限管理
- [ ] 分析与使用统计
- [ ] 模型微调和优化
- [ ] 云平台部署

---

## 参考资源

- [LlamaIndex 文档](https://docs.llamaindex.ai/)
- [BM25 算法](https://en.wikipedia.org/wiki/Okapi_BM25)
- [FAISS 向量数据库](https://github.com/facebookresearch/faiss)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

## 文档更新日志

| 日期 | 版本 | 更新内容 |
|------|------|--------|
| 2026-04-04 | 1.0 | 初始版本：完整的混合检索RAG执行计划 |

---

**最后更新**：2026-04-04  
**维护者**：COMP7125 Group Project  
**状态**：✅ Ready for Implementation
