from fastapi import APIRouter, Depends, HTTPException, Path, Request
from typing import List
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.limiter import limiter
from app.dependencies import get_db, get_current_user


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.post("/", response_model=schemas.Project)
@limiter.limit("5/minute")
def create_project(
    request: Request,
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.create_project(db=db, project=project, user_id=current_user.id)


@router.get("/", response_model=List[schemas.Project])
@limiter.limit("5/minute")
def read_projects(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=schemas.Project)
@limiter.limit("5/minute")
def read_project(
    request: Request,
    project_id: int = Path(..., description="The ID of the project to retrieve"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=schemas.Project)
@limiter.limit("5/minute")
def update_project(
    request: Request,
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.update_project(db, db_project, project_update)

@router.delete("/{project_id}", response_model=schemas.Project)
@limiter.limit("5/minute")
def delete_project(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    crud.delete_project(db, db_project)
    return db_project

@router.get("/", response_model=List[schemas.Project])
@limiter.limit("5/minute")
def read_projects(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    projects = (
        db.query(models.Project)
        .filter(models.Project.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return projects
