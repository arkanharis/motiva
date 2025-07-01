from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ScheduleBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    status: Optional[str] = "scheduled"
    schedule_type: Optional[str] = "meeting"
    is_recurring: Optional[bool] = False
    recurring_pattern: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    status: Optional[str] = None
    schedule_type: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_pattern: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema untuk list schedules dengan filter
class ScheduleFilter(BaseModel):
    status: Optional[str] = None
    schedule_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0