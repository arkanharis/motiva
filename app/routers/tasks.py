from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.task import (
    Task, TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskPriority, TaskStatus
)
from ..services.task_service import TaskService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Membuat task baru"""
    db_task = TaskService.create_task(db, task, current_user.id)
    return TaskResponse(message="Task berhasil dibuat", task=db_task)

@router.get("/", response_model=TaskListResponse)
def get_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of tasks to return"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan daftar task dengan filter dan pagination"""
    tasks, total = TaskService.get_tasks(
        db, current_user.id, skip, limit, status, priority, search
    )
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=(skip // limit) + 1,
        size=len(tasks)
    )

@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan detail task berdasarkan ID"""
    task = TaskService.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task tidak ditemukan"
        )
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task"""
    updated_task = TaskService.update_task(db, task_id, task_update, current_user.id)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task tidak ditemukan"
        )
    return TaskResponse(message="Task berhasil diupdate", task=updated_task)

@router.delete("/{task_id}", response_model=dict)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hapus task"""
    success = TaskService.delete_task(db, task_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task tidak ditemukan"
        )
    return {"message": "Task berhasil dihapus"}

@router.patch("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task_completion(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle status completed task"""
    task = TaskService.toggle_task_completion(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task tidak ditemukan"
        )
    
    status_msg = "selesai" if task.is_completed else "belum selesai"
    return TaskResponse(message=f"Task berhasil diubah menjadi {status_msg}", task=task)

@router.get("/overdue/list", response_model=List[Task])
def get_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan task yang sudah lewat due date"""
    tasks = TaskService.get_overdue_tasks(db, current_user.id)
    return tasks

@router.get("/upcoming/list", response_model=List[Task])
def get_upcoming_tasks(
    days: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan task yang akan datang dalam beberapa hari"""
    tasks = TaskService.get_upcoming_tasks(db, current_user.id, days)
    return tasks

@router.get("/stats/summary", response_model=dict)
def get_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mendapatkan statistik task user"""
    from sqlalchemy import func
    from ..models.task import Task
    
    # Query statistik
    stats = db.query(
        func.count(Task.id).label('total'),
        func.count(Task.id).filter(Task.is_completed == True).label('completed'),
        func.count(Task.id).filter(Task.is_completed == False).label('pending'),
        func.count(Task.id).filter(Task.priority == 'high').label('high_priority'),
    ).filter(Task.user_id == current_user.id).first()
    
    # Task overdue
    overdue_count = len(TaskService.get_overdue_tasks(db, current_user.id))
    
    return {
        "total_tasks": stats.total or 0,
        "completed_tasks": stats.completed or 0,
        "pending_tasks": stats.pending or 0,
        "high_priority_tasks": stats.high_priority or 0,
        "overdue_tasks": overdue_count,
        "completion_rate": round((stats.completed / stats.total * 100) if stats.total > 0 else 0, 2)
    }