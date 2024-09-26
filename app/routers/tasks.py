from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud, models
from app.limiter import limiter
from app.routers.notifications import broadcast_message
from app.dependencies import get_db, get_current_user


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post("/", response_model=schemas.Task)
@limiter.limit("5/minute")
def create_task(
    request: Request,
    task: schemas.TaskCreate,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    broadcast_message(f"Task {task.title} created");
    return crud.create_task(
        db=db, task=task, user_id=current_user.id, project_id=project_id
    )


@router.get("/", response_model=List[schemas.Task])
@limiter.limit("5/minute")
def read_tasks(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/{task_id}", response_model=schemas.Task)
@limiter.limit("5/minute")
def read_task(
    request: Request,
    task_id: int = Path(..., description="The ID of the task to retrieve"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=schemas.Task)
@limiter.limit("5/minute")
def update_task(
    request: Request, 
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    broadcast_message(f"Task {db_task.title} updated");
    return crud.update_task(db, db_task, task_update)

@router.delete("/{task_id}", response_model=schemas.Task)
@limiter.limit("5/minute")
def delete_task(
    request: Request, 
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, db_task)
    return db_task

@router.get("/", response_model=List[schemas.Task])
@limiter.limit("5/minute")
def read_tasks(
    request: Request, 
    skip: int = 0,
    limit: int = 10,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    query = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    if is_completed is not None:
        query = query.filter(models.Task.is_completed == is_completed)
    tasks = query.offset(skip).limit(limit).all()
    return tasks
