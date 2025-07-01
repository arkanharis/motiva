from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from ..models.task import Task
from ..models.user import User
from ..schemas.task import TaskCreate, TaskUpdate, TaskStatus

class TaskService:
    
    @staticmethod
    def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
        """Membuat task baru"""
        db_task = Task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            reminder_time=task.reminder_time,
            user_id=user_id
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """Mendapatkan task berdasarkan ID dan user_id"""
        return db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
    
    @staticmethod
    def get_tasks(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Task], int]:
        """Mendapatkan daftar task dengan filter dan pagination"""
        query = db.query(Task).filter(Task.user_id == user_id)
        
        # Filter berdasarkan status
        if status:
            query = query.filter(Task.status == status)
        
        # Filter berdasarkan priority
        if priority:
            query = query.filter(Task.priority == priority)
        
        # Search dalam title atau description
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )
        
        # Hitung total
        total = query.count()
        
        # Order by created_at desc dan apply pagination
        tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
        
        return tasks, total
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[Task]:
        """Update task"""
        db_task = TaskService.get_task_by_id(db, task_id, user_id)
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        
        # Handle status change logic
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == TaskStatus.completed:
                update_data["is_completed"] = True
                update_data["completed_at"] = datetime.utcnow()
            elif db_task.status == TaskStatus.completed and new_status != TaskStatus.completed:
                update_data["is_completed"] = False
                update_data["completed_at"] = None
        
        # Handle is_completed change
        if "is_completed" in update_data:
            if update_data["is_completed"]:
                update_data["status"] = TaskStatus.completed
                update_data["completed_at"] = datetime.utcnow()
            else:
                if db_task.status == TaskStatus.completed:
                    update_data["status"] = TaskStatus.pending
                update_data["completed_at"] = None
        
        # Update fields
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> bool:
        """Hapus task"""
        db_task = TaskService.get_task_by_id(db, task_id, user_id)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    @staticmethod
    def toggle_task_completion(db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """Toggle status completed task"""
        db_task = TaskService.get_task_by_id(db, task_id, user_id)
        if not db_task:
            return None
        
        if db_task.is_completed:
            db_task.is_completed = False
            db_task.status = TaskStatus.pending
            db_task.completed_at = None
        else:
            db_task.is_completed = True
            db_task.status = TaskStatus.completed
            db_task.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_overdue_tasks(db: Session, user_id: int) -> List[Task]:
        """Mendapatkan task yang sudah lewat due date"""
        now = datetime.utcnow()
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.is_completed == False
            )
        ).all()
    
    @staticmethod
    def get_upcoming_tasks(db: Session, user_id: int, days: int = 7) -> List[Task]:
        """Mendapatkan task yang akan datang dalam beberapa hari"""
        from datetime import timedelta
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.due_date >= now,
                Task.due_date <= future,
                Task.is_completed == False
            )
        ).order_by(Task.due_date).all()