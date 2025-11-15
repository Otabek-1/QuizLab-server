from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.db import get_db, Question, Test, Option
from schemas.question import QuestionCreate

router = APIRouter(prefix="/questions")

@router.get("/{test_id}")
def get_questions(test_id:int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    return {"questions": questions}

@router.post("/")
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    try:
        new_question = Question(
            test_id=question.test_id,
            text=question.text,
            image_url=question.image_url,
            question_type=question.question_type,
            correct_answer_text=question.correct_answer_text
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        return {"question": new_question}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{question_id}")
def update_question(question_id: int, question: QuestionCreate, db: Session = Depends(get_db)):
    existing_question = db.query(Question).filter(Question.id == question_id).first()
    if not existing_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    try:
        existing_question.text = question.text
        existing_question.image_url = question.image_url
        existing_question.question_type = question.question_type
        existing_question.correct_answer_text = question.correct_answer_text
        db.commit()
        db.refresh(existing_question)
        return {"question": existing_question}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    existing_question = db.query(Question).filter(Question.id == question_id).first()
    if not existing_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    try:
        db.delete(existing_question)
        db.commit()
        return {"detail": "Question deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))