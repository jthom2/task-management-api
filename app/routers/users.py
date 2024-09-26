from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app import schemas, crud
from app.limiter import limiter
from app.dependencies import get_db, get_password_hash, get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=schemas.User)
@limiter.limit("5/minute")
def create_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

@router.get(
    "/me",
    response_model=schemas.User,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("5/minute")
def read_users_me(request: Request, current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.delete("/{user_id}", dependencies=[Depends(get_current_admin_user)])
@limiter.limit("5/minute")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db, db_user)

@router.delete("/{user_id}", dependencies=[Depends(get_current_admin_user)])
@limiter.limit("5/minute")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db, db_user)