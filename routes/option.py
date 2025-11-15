from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.db import get_db, Question, Test, Option
from schemas.option import OptionCreate

router = APIRouter(prefix="/options")

@router.get("/{question_id}")
def get_options(question_id:int, db: Session = Depends(get_db)):
    options = db.query(Option).filter(Option.question_id == question_id).all()
    return {"options": options}

@router.post("/")
def create_option(option: OptionCreate, db: Session = Depends(get_db)):
    try:
        new_option = Option(
            question_id=option.question_id,
            text=option.text,
            is_correct=option.is_correct
        )
        db.add(new_option)
        db.commit()
        db.refresh(new_option)
        return {"option": new_option}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{option_id}")
def update_option(option_id: int, option: OptionCreate, db: Session = Depends(get_db)):
    existing_option = db.query(Option).filter(Option.id == option_id).first()
    if not existing_option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
    try:
        existing_option.text = option.text
        existing_option.is_correct = option.is_correct
        db.commit()
        db.refresh(existing_option)
        return {"option": existing_option}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{option_id}")
def delete_option(option_id: int, db: Session = Depends(get_db)):
    existing_option = db.query(Option).filter(Option.id == option_id).first()
    if not existing_option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
    try:
        db.delete(existing_option)
        db.commit()
        return {"detail": "Option deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))