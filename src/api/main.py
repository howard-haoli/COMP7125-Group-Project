"""
FastAPI主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="ReAct课程管理系统",
    description="基于ReAct和RAG的智能课程管理和可视化系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根端点 - 健康检查"""
    return {
        "status": "running",
        "service": "ReAct Course Management System",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": str(datetime.now())
    }


@app.post("/api/schedule/generate")
async def generate_schedule(user_query: str, include_excel: bool = True):
    """
    生成课表和统计图表
    
    Args:
        user_query: 用户查询
        include_excel: 是否包含Excel导出
    """
    return {
        "success": True,
        "message": "Schedule generation started",
        "status": "processing"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
