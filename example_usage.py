#!/usr/bin/env python
"""
示例脚本 - 演示如何使用ReAct引擎和工具

使用方法:
    python example_usage.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.react_engine import ReActEngine
from src.tools.rag_tool import retrieve_course_info
from src.tools.schedule_optimizer import optimize_schedule
from src.utils.types import Course


def example_1_basic_react_engine():
    """示例1: 基础ReAct引擎演示"""
    print("\n" + "="*60)
    print("示例 1: 基础 ReAct 引擎")
    print("="*60)
    
    # 创建ReAct引擎
    engine = ReActEngine()
    print(f"✅ ReAct引擎已创建，最大迭代次数: {engine.max_iterations}")
    
    # 模拟用户查询
    user_query = "生成本周课表"
    print(f"📝 用户查询: {user_query}")
    
    # 运行ReAct循环
    result = engine.run(user_query)
    
    print(f"\n📊 执行结果:")
    print(f"   - 成功: {result.success}")
    print(f"   - 执行步数: {result.current_step}")
    print(f"   - 思考次数: {len(result.thoughts)}")
    print(f"   - 行动次数: {len(result.actions)}")
    print(f"   - 观察次数: {len(result.observations)}")


def example_2_rag_retrieval():
    """示例2: RAG课程检索演示"""
    print("\n" + "="*60)
    print("示例 2: RAG 课程检索")
    print("="*60)
    
    # 执行RAG查询
    query = "周一的计算机科学课程"
    print(f"🔍 搜索查询: {query}")
    
    result = retrieve_course_info(
        query=query,
        semester="Spring2026",
        limit=5
    )
    
    print(f"\n📚 检索结果:")
    print(f"   - 成功: {result['success']}")
    print(f"   - 找到课程数: {result['total_count']}")
    print(f"   - 搜索时间: {result['metadata']['timestamp']}")
    

def example_3_schedule_optimization():
    """示例3: 排课优化演示"""
    print("\n" + "="*60)
    print("示例 3: 排课优化")
    print("="*60)
    
    # 创建示例课程数据
    sample_courses = [
        {
            "id": "CS101",
            "name": "Data Structures",
            "teacher": "Dr. Smith",
            "room": "Room 101",
            "day": "Monday",
            "start_time": "09:00",
            "duration": 90,
            "capacity": 50,
            "type": "lecture"
        },
        {
            "id": "CS102",
            "name": "Algorithms",
            "teacher": "Dr. Johnson",
            "room": "Room 102",
            "day": "Tuesday",
            "start_time": "10:00",
            "duration": 90,
            "capacity": 40,
            "type": "lecture"
        }
    ]
    
    print(f"📋 输入课程数: {len(sample_courses)}")
    
    # 执行排课优化
    result = optimize_schedule(
        courses=sample_courses,
        constraints={"no_conflicts": True},
        algorithm="greedy"
    )
    
    print(f"\n✨ 优化结果:")
    print(f"   - 成功: {result['success']}")
    print(f"   - 输出课程数: {len(result['courses_optimized'])}")
    print(f"   - 解决冲突数: {result['conflicts_resolved']}")
    print(f"   - 总结: {result['summary']}")


def example_4_data_models():
    """示例4: 数据模型演示"""
    print("\n" + "="*60)
    print("示例 4: 数据模型")
    print("="*60)
    
    # 创建Course对象
    course = Course(
        id="CS201",
        name="Machine Learning",
        teacher="Dr. Williams",
        room="Lab 201",
        day="Wednesday",
        start_time="14:00",
        duration=120,
        capacity=30,
        department="Computer Science",
        students_enrolled=28,
        credits=4.0
    )
    
    print(f"📚 创建的课程对象:")
    print(f"   - ID: {course.id}")
    print(f"   - 名称: {course.name}")
    print(f"   - 讲师: {course.teacher}")
    print(f"   - 教室: {course.room}")
    print(f"   - 时间: {course.day} {course.start_time}")
    print(f"   - 容量: {course.capacity}")
    print(f"   - 已登记: {course.students_enrolled}")
    print(f"   - 学分: {course.credits}")


def example_5_full_workflow():
    """示例5: 完整工作流演示"""
    print("\n" + "="*60)
    print("示例 5: 完整 ReAct 工作流")
    print("="*60 + "\n")
    
    print("""
    这是一个完整的ReAct工作流演示:
    
    1️⃣  用户输入: "给我生成本周课表"
    
    2️⃣  ReAct引擎开始执行:
    
       思考 1: "需要获取本周的课程数据"
       ↓
       行动 1: retrieve_course_info(query="本周课程")
       ↓
       观察 1: 返回15门课程
       
       思考 2: "检查是否有时间冲突"
       ↓
       行动 2: optimize_schedule(courses=...)
       ↓
       观察 2: 0个冲突已解决
       
       思考 3: "生成可视化"
       ↓
       行动 3: generate_timetable_local(courses=...)
       ↓
       观察 3: 已生成 timetable.png
       
       思考 4: "任务完成"
       ↓
       行动 4: STOP
    
    3️⃣  系统返回:
        ✅ 课表已生成: timetable.png
        ✅ 共15门课程，0个冲突
        📊 周一: 4门课，周二: 5门课...
    """)


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════════════════════════╗
║         ReAct 课程系统 - 使用示例演示                      ║
║         COMP7125 Group Project                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    examples = {
        "1": ("基础ReAct引擎", example_1_basic_react_engine),
        "2": ("RAG课程检索", example_2_rag_retrieval),
        "3": ("排课优化", example_3_schedule_optimization),
        "4": ("数据模型", example_4_data_models),
        "5": ("完整工作流", example_5_full_workflow),
        "all": ("运行全部示例", None),
        "exit": ("退出", None)
    }
    
    while True:
        print("\n📋 可用示例:")
        for key, (name, _) in examples.items():
            print(f"   {key}. {name}")
        
        choice = input("\n请选择 (1-5, all, 或 exit): ").strip().lower()
        
        if choice == "exit":
            print("\n👋 再见!")
            break
        elif choice == "all":
            example_1_basic_react_engine()
            example_2_rag_retrieval()
            example_3_schedule_optimization()
            example_4_data_models()
            example_5_full_workflow()
        elif choice in examples and examples[choice][1]:
            examples[choice][1]()
        else:
            print("❌ 无效选择，请重试")


if __name__ == "__main__":
    main()
