from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class ActivityStatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"

class CategoryEnum(str, Enum):
    tarea = "tarea"
    examen = "examen"
    proyecto = "proyecto"
    presentacion = "presentacion"
    laboratorio = "laboratorio"
    ensayo = "ensayo"
    investigacion = "investigacion"

# Modelos para Estudiantes
class StudentBase(BaseModel):
    name: str
    email: EmailStr
    career: str
    semester: int
    status: StatusEnum = StatusEnum.active

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    avatar: str

    class Config:
        from_attributes = True

class ActivityBase(BaseModel):
    title: str
    subject: str
    description: str
    due_date: str
    priority: PriorityEnum = PriorityEnum.medium
    status: ActivityStatusEnum = ActivityStatusEnum.pending
    category: CategoryEnum = CategoryEnum.tarea
    estimated_hours: Optional[int] = None
    tags: List[str] = []

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[ActivityStatusEnum] = None
    category: Optional[CategoryEnum] = None
    estimated_hours: Optional[int] = None
    tags: Optional[List[str]] = None

class Activity(ActivityBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    active_students: int
    general_average: float
    pending_submissions: int
    attendance: int

class WeeklyProgress(BaseModel):
    week: str
    value: float

class GradeDistribution(BaseModel):
    name: str
    value: int
    color: str

class Alert(BaseModel):
    id: int
    type: str
    title: str
    description: str
    action: str

class DashboardData(BaseModel):
    stats: DashboardStats
    weekly_progress: List[WeeklyProgress]
    grade_distribution: List[GradeDistribution]
    alerts: List[Alert]

class MessageBase(BaseModel):
    sender: str
    content: str
    is_own: bool = False

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: str
    avatar: str

    class Config:
        from_attributes = True

class User(BaseModel):
    id: int
    name: str
    status: str
    avatar: str

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None