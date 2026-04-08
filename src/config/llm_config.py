"""
LLM配置文件 - Ollama和其他LLM服务的配置
"""

import os
from typing import Dict, Any

# ============ Ollama LLM配置 ============

LLM_CONFIG: Dict[str, Any] = {
    "type": "ollama",
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "model": os.getenv("LLM_MODEL", "llama2:13b"),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
    "top_p": 0.9,
    "top_k": 40,
    "max_tokens": 2048,
    "timeout": 60,

    # ReAct特定配置
    "react": {
        "max_iterations": 5,
        "timeout_per_iteration": 30,
        "stop_phrases": ["Final Answer:", "完成", "STOP"],
        "enable_thought_logging": True
    },

    # 流式响应配置
    "stream": {
        "enabled": True,
        "chunk_size": 256
    }
}

# ============ RAG相关LLM配置 ============

RAG_EMBEDDING_CONFIG: Dict[str, Any] = {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "device": os.getenv("EMBEDDING_DEVICE", "cpu"),
    "normalize_embeddings": True,
    "dimension": 384
}

# ============ 系统提示词模板 ============

SYSTEM_PROMPTS: Dict[str, str] = {
    "course_scheduling": """You are an intelligent course scheduling assistant. 
Your task is to help users manage and visualize course information.

Available tools:
1. retrieve_course_info - Get course data from RAG database
2. optimize_schedule - Resolve scheduling conflicts
3. generate_timetable_local - Create timetable images
4. generate_statistics_local - Generate analysis charts
5. export_to_excel - Export to Excel format

Follow this format:
Thought: [Your analysis]
Action: [Tool call in JSON]
Observation: [Result]
...
Final Answer: [Summary]

Always be specific and use all available information.""",

    "rag_query_expansion": """Expand the user's query to include relevant variations and synonyms
to improve retrieval quality. Return a list of expanded queries."""
}
