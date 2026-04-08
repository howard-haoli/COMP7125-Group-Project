"""
ReAct框架核心引擎 - 思考-行动-观察循环实现

本模块实现了ReAct (Reasoning + Acting) 框架的核心逻辑,
支持多轮推理、工具调用和结果反馈的完整循环。
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


# ========== 数据模型定义 ==========

class ActionType(Enum):
    """Action类型枚举"""
    TOOL_CALL = "tool_call"
    STOP = "stop"
    CONTINUE = "continue"


@dataclass
class Thought:
    """思考步骤"""
    content: str                    # 思考内容
    timestamp: datetime = field(default_factory=datetime.now)
    reasoning_type: str = "general" # 推理类型
    confidence: float = 1.0         # 置信度 0-1


@dataclass
class Action:
    """行动步骤"""
    type: ActionType
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps({
            "type": self.type.value,
            "tool_name": self.tool_name,
            "parameters": self.parameters
        })


@dataclass
class Observation:
    """观察步骤"""
    tool_name: str
    status: str                    # "success" or "failed"
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReActState:
    """ReAct执行状态"""
    user_query: str
    thoughts: List[Thought] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    observations: List[Observation] = field(default_factory=list)
    current_step: int = 0
    final_answer: Optional[str] = None
    success: bool = False
    output_files: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


# ========== ReAct引擎实现 ==========

class ReActEngine:
    """
    ReAct引擎 - 协调思考、行动和观察的循环
    
    使用示例:
        engine = ReActEngine()
        result = engine.run("生成本周课表")
        print(result.final_answer)
    """
    
    def __init__(self, llm_config: Optional[Dict] = None):
        """
        初始化ReAct引擎
        
        Args:
            llm_config: LLM配置字典
        """
        self.config = llm_config or {}
        self.logger = logging.getLogger(__name__)
        self.tool_registry: Dict[str, Callable] = {}
        self.max_iterations = self.config.get("react", {}).get("max_iterations", 5)
        self.llm = None  # 初始化占位符
        
    def _initialize_llm(self):
        """初始化LLM客户端"""
        try:
            from langchain_community.llms import Ollama
            
            llm = Ollama(
                base_url=self.config.get("base_url", "http://localhost:11434"),
                model=self.config.get("model", "llama2:13b"),
                temperature=self.config.get("temperature", 0.7),
                num_ctx=4096
            )
            return llm
        except Exception as e:
            self.logger.error(f"LLM initialization failed: {e}")
            return None
    
    def register_tool(self, tool_name: str, tool_func: Callable) -> None:
        """
        注册可用工具
        
        Args:
            tool_name: 工具名称
            tool_func: 可调用的工具函数
        """
        self.tool_registry[tool_name] = tool_func
        self.logger.info(f"Tool registered: {tool_name}")
    
    def run(self, user_query: str) -> ReActState:
        """
        运行ReAct循环
        
        Args:
            user_query: 用户问题
            
        Returns:
            ReActState: 执行状态和结果
        """
        state = ReActState(user_query=user_query)
        self.logger.info(f"Starting ReAct loop for query: {user_query}")
        
        for iteration in range(self.max_iterations):
            state.current_step = iteration + 1
            
            # 1. 思考 (Thought)
            thought = self._think(state)
            state.thoughts.append(thought)
            self.logger.info(f"Iteration {state.current_step} - Thought: {thought.content[:100]}")
            
            # 2. 规划行动 (Action)
            action = self._plan_action(state, thought)
            state.actions.append(action)
            
            if action.type == ActionType.STOP:
                state.final_answer = action.parameters.get("answer", "")
                state.success = True
                self.logger.info("ReAct loop finished with STOP action")
                break
            
            # 3. 执行行动并观察 (Observation)
            observation = self._execute_action(action)
            state.observations.append(observation)
            
            if observation.status == "failed":
                self.logger.warning(f"Action failed: {observation.error}")
        
        state.end_time = datetime.now()
        return state
    
    def _think(self, state: ReActState) -> Thought:
        """
        LLM思考步骤
        
        Args:
            state: 当前执行状态
            
        Returns:
            Thought: 思考内容
        """
        context = f"用户问题: {state.user_query}\n当前进度: {state.current_step}/{self.max_iterations}"
        
        # TODO: 集成具体的LLM推理逻辑
        thought_content = f"思考步骤 {state.current_step}: 分析问题结构"
        
        return Thought(content=thought_content)
    
    def _plan_action(self, state: ReActState, thought: Thought) -> Action:
        """
        根据思考规划行动
        
        Args:
            state: 当前执行状态
            thought: 思考内容
            
        Returns:
            Action: 规划的行动
        """
        if state.current_step >= self.max_iterations:
            return Action(type=ActionType.STOP, parameters={"answer": "已达最大迭代次数"})
        
        # TODO: 实现工具选择逻辑
        return Action(type=ActionType.CONTINUE)
    
    def _execute_action(self, action: Action) -> Observation:
        """
        执行规划的行动
        
        Args:
            action: 规划的行动
            
        Returns:
            Observation: 执行结果观察
        """
        if action.type == ActionType.STOP:
            return Observation(
                tool_name="system",
                status="success",
                result="Task completed"
            )
        
        if action.tool_name and action.tool_name in self.tool_registry:
            try:
                import time
                start = time.time()
                
                tool_func = self.tool_registry[action.tool_name]
                result = tool_func(**action.parameters)
                
                execution_time = (time.time() - start) * 1000
                
                return Observation(
                    tool_name=action.tool_name,
                    status="success",
                    result=result,
                    execution_time_ms=execution_time
                )
            except Exception as e:
                self.logger.error(f"Tool execution error: {e}")
                return Observation(
                    tool_name=action.tool_name,
                    status="failed",
                    result=None,
                    error=str(e)
                )
        
        return Observation(
            tool_name=action.tool_name or "unknown",
            status="failed",
            result=None,
            error="Tool not found or action skipped"
        )
