from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    is_completed: Optional[bool] = None

class Task(TaskBase):
    id: int
    status: TaskStatus
    is_completed: bool
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    message: str
    task: Optional[Task] = None

class TaskListResponse(BaseModel):
    tasks: list[Task]
    total: int
    page: int
    size: int