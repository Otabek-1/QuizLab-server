from db.db import Test, User, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.auth import get_user_info
from schemas.test import TestCreate

router = APIRouter(prefix="/tests")

@router.get("/")
def get_tests(db: Session = Depends(get_db), token: str = Depends(get_user_info)):
    tg_id, user_id = token.split("&")
    tests = db.query(Test).filter(Test.created_by == int(user_id)).all()
    return {"tests": tests}

@router.get("/{test_id}")
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return {"test": test}

@router.post("/")
def create_test(test:TestCreate,db: Session = Depends(get_db), token: str = Depends(get_user_info)):
    tg_id, user_id = token.split("&")
    try:
        new_test = Test(title=test.title, description=test.description, created_by=int(user_id), duration_minutes=test.duration_minutes, max_attempts=test.max_attempts)
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return {"test": new_test}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{test_id}")
def update_test(test_id: int, test: TestCreate, db: Session = Depends(get_db), token: str = Depends(get_user_info)):
    tg_id, user_id = token.split("&")
    existing_test = db.query(Test).filter(Test.id == test_id, Test.created_by == int(user_id)).first()
    if not existing_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    try:
        existing_test.title = test.title
        existing_test.description = test.description
        existing_test.duration_minutes = test.duration_minutes
        existing_test.max_attempts = test.max_attempts
        db.commit()
        db.refresh(existing_test)
        return {"test": existing_test}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{test_id}")
def delete_test(test_id: int, db: Session = Depends(get_db), token: str = Depends(get_user_info)):
    tg_id, user_id = token.split("&")
    existing_test = db.query(Test).filter(Test.id == test_id, Test.created_by == int(user_id)).first()
    if not existing_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    try:
        db.delete(existing_test)
        db.commit()
        return {"detail": "Test deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))