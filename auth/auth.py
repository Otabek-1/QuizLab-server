from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.db import get_db, User
from schemas.user import User as UserSchema, Login
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth")

secret_key = "quizlab_secret_key_1324"
security = HTTPBearer()

def create_access_token(data: dict, expires_delte: timedelta = None):
    to_encode = data.copy()
    if expires_delte:
        expire = datetime.utcnow() + expires_delte
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp":expire})
    token = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return token

def get_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        tg_id: str = payload.get("sub")
        if tg_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return tg_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@router.post("/register")
def register_user(data: UserSchema, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.tg_id == str(data.tg_id)).first()
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        new_user = User(tg_id=data.tg_id, username=data.username)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        access_token = create_access_token(data={"sub": f"{new_user.tg_id}&{new_user.id}"})
        return {"user": new_user, "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login")
def login_user(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.tg_id == str(data.tg_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    access_token = create_access_token(data={"sub": f"{user.tg_id}&{user.id}"})
    return {"user": user, "access_token": access_token}