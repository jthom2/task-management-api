from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import Body
from jose import JWTError, jwt
from app import schemas, crud, main
from app.limiter import limiter
from app.dependencies import SECRET_KEY, ALGORITHM, get_db, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

REFRESH_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_MINUTES = 15

@router.post("/token", response_model=schemas.Token)
@limiter.limit("5/minute")
def login_for_access_token(
    request: Request,
    login_data: schemas.LoginData, db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        main.logger.warning(f"Failed login attempt for user: {login_data.username}")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    main.logger.info(f"User logged in: {login_data.username}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token,
             "token_type": "bearer",
             "refresh_token": "refresh_token",
             }

@router.post("/token/refresh", response_model=schemas.Token)
@limiter.limit("5/minute")
def refresh_access_token(
    request: Request,
    refresh_token: str = Body(...), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
