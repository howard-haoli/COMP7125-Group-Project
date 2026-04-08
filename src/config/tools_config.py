"""
工具配置文件 - 所有工具的参数配置
"""

import os
from typing import Dict, Any

TOOLS_CONFIG: Dict[str, Any] = {
    # ========== RAG工具配置 ==========
    "rag": {
        "vector_db": "chromadb",
        "db_path": os.getenv("CHROMA_DB_PATH", "./data/chroma_db"),
        "model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        "chunk_size": 500,
        "chunk_overlap": 50,
        "search_limit": 50,
        "similarity_threshold": 0.5
    },

    # ========== 排课优化工具配置 ==========
    "schedule_optimizer": {
        "algorithm": "greedy",  # "greedy" 或 "hungarian"
        "conflict_check": True,
        "max_continuous_hours": 4,
        "min_break_minutes": 15,
        "room_capacity_check": True
    },

    # ========== 本地可视化配置 ==========
    "visualization": {
        "local": {
            "matplotlib": {
                "dpi": 300,
                "figsize": (16, 9),
                "style": "default",
                "time_granularity": "30min",
                "colors": {
                    "lecture": "#FF6B6B",
                    "lab": "#4ECDC4",
                    "seminar": "#45B7D1",
                    "other": "#96CEB4"
                }
            },
            "plotly": {
                "format": "png",
                "width": 1200,
                "height": 600,
                "template": "plotly_white"
            }
        },

        # ========== 在线API服务配置 ==========
        "online": {
            "mermaid": {
                "api": "https://mermaid.ink/img/",
                "timeout": 30,
                "retry_count": 3
            },
            "plotly": {
                "api": "https://api.plot.ly/v2/",
                "timeout": 30,
                "format": "png"
            }
        }
    },

    # ========== 文件输出配置 ==========
    "output": {
        "base_dir": "./data/output",
        "timetable_dir": "./data/output/timetables",
        "stats_dir": "./data/output/statistics",
        "excel_dir": "./data/output/excel",
        "file_prefix": "course_",
        "timestamp_format": "%Y%m%d_%H%M%S"
    }
}
