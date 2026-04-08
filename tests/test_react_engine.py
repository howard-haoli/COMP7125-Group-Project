"""
基础测试 - ReAct引擎功能测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.react_engine import ReActEngine, ActionType, Thought, Action, Observation
import pytest


def test_react_engine_init():
    """测试ReAct引擎初始化"""
    engine = ReActEngine()
    assert engine is not None
    assert engine.max_iterations == 5


def test_thought_creation():
    """测试Thought创建"""
    thought = Thought(content="Test thought")
    assert thought.content == "Test thought"
    assert thought.reasoning_type == "general"
    assert thought.confidence == 1.0


def test_action_creation():
    """测试Action创建"""
    action = Action(type=ActionType.TOOL_CALL, tool_name="test_tool")
    assert action.type == ActionType.TOOL_CALL
    assert action.tool_name == "test_tool"


def test_observation_creation():
    """测试Observation创建"""
    observation = Observation(
        tool_name="test_tool",
        status="success",
        result={"data": "test"}
    )
    assert observation.tool_name == "test_tool"
    assert observation.status == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
