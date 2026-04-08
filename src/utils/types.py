"""
类型定义 - 系统中使用的数据结构
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CourseType(Enum):
    """课程类型"""
    LECTURE = "lecture"
    LAB = "lab"
    SEMINAR = "seminar"
    WORKSHOP = "workshop"
    OTHER = "other"


@dataclass
class Course:
    """
    课程信息
    
    Attributes:
        id: 课程ID
        name: 课程名称
        teacher: 授课教师
        room: 教室编号
        day: 上课日期 (Monday-Sunday)
        start_time: 开始时间 (HH:MM格式)
        duration: 课程时长(分钟)
        capacity: 教室容量
        type: 课程类型 (Lecture/Lab/Seminar等)
    """
    id: str
    name: str
    teacher: str
    room: str
    day: str
    start_time: str
    duration: int
    capacity: int
    type: CourseType = CourseType.LECTURE
    semester: str = "current"
    department: Optional[str] = None
    students_enrolled: int = 0
    credits: float = 3.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """后处理 - 类型转换"""
        if isinstance(self.type, str):
            self.type = CourseType(self.type)


@dataclass
class TimeSlot:
    """时间段"""
    day: str
    start_time: str
    end_time: str


@dataclass
class Room:
    """教室信息"""
    room_id: str
    building: str
    capacity: int
    equipment: List[str] = field(default_factory=list)


@dataclass
class Teacher:
    """教师信息"""
    teacher_id: str
    name: str
    department: str
    courses: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """数据验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)
