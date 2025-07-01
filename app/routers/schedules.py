from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schedule import Schedule
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleFilter
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(
    prefix="/schedules",
    tags=["schedules"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ScheduleResponse)
def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new schedule for the current user"""
    db_schedule = Schedule(
        **schedule.dict(),
        user_id=current_user.id
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.get("/", response_model=List[ScheduleResponse])
def get_schedules(
    status: Optional[str] = Query(None, description="Filter by status"),
    schedule_type: Optional[str] = Query(None, description="Filter by schedule type"),
    start_date: Optional[datetime] = Query(None, description="Filter schedules from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter schedules until this date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all schedules for the current user with optional filters"""
    query = db.query(Schedule).filter(Schedule.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Schedule.status == status)
    if schedule_type:
        query = query.filter(Schedule.schedule_type == schedule_type)
    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.start_time <= end_date)
    
    # Order by start_time and apply pagination
    schedules = query.order_by(Schedule.start_time).offset(offset).limit(limit).all()
    return schedules

@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific schedule by ID"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific schedule"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Update only provided fields
    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific schedule"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}

@router.get("/today/", response_model=List[ScheduleResponse])
def get_today_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all schedules for today"""
    from datetime import date
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    schedules = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        Schedule.start_time >= today_start,
        Schedule.start_time <= today_end
    ).order_by(Schedule.start_time).all()
    
    return schedules

@router.get("/upcoming/", response_model=List[ScheduleResponse])
def get_upcoming_schedules(
    days: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming schedules for the next N days"""
    from datetime import date, timedelta
    today = date.today()
    end_date = today + timedelta(days=days)
    
    schedules = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        Schedule.start_time >= datetime.combine(today, datetime.min.time()),
        Schedule.start_time <= datetime.combine(end_date, datetime.max.time()),
        Schedule.status.in_(["scheduled", "ongoing"])
    ).order_by(Schedule.start_time).all()
    
    return schedules