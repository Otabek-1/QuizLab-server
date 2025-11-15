from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.db import get_db, Question, Test, Option, Attempt, AttemptAnswer
from schemas.attempt import AttemptCreate, AttemptAnswerCreate
from datetime import datetime

router = APIRouter(prefix="/attempts")
security = HTTPBearer()

@router.get("/test/{test_id}")
def get_attempts_by_test(test_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    attempts = db.query(Attempt).filter(Attempt.test_id == test_id).all()
    return attempts

@router.get('/user/{user_id}')
def get_attempts_by_user(user_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    attempts = db.query(Attempt).filter(Attempt.user_id == user_id).all()
    return attempts

@router.post('/')
def create_attempt(
    attempt: AttemptCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    test = db.query(Test).filter(Test.id == attempt.test_id).first()
    if not test:
        raise HTTPException(404, "Test not found")

    # 🌟 Max attempts tekshirish
    if test.max_attempts is not None:
        used_attempts = db.query(Attempt).filter(
            Attempt.test_id == test.id,
            Attempt.user_id == attempt.user_id
        ).count()

        if used_attempts >= test.max_attempts:
            raise HTTPException(400, "Attempt limit reached")

    # 🌟 Start attempt
    new_attempt = Attempt(
        test_id=attempt.test_id,
        user_id=attempt.user_id,
        started_at=datetime.utcnow(),
        finished_at=None,
        score=0
    )

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)
    return new_attempt


@router.delete('/{attempt_id}')
def delete_attempt(attempt_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    db.delete(attempt)
    db.commit()
    return {"detail": "Attempt deleted successfully"}

@router.post('/answer/create')
def create_attempt_answer(
    answer: AttemptAnswerCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    if not question:
        raise HTTPException(404, "Question not found")

    is_correct = False

    # 🌟 Test-savol turi bo‘yicha baholash
    if question.question_type in ["single_choice", "multi_choice"]:
        option = db.query(Option).filter(Option.id == answer.selected_option_id).first()
        is_correct = option.is_correct if option else False

    elif question.question_type == "short_answer":
        if question.correct_answer_text:
            is_correct = (
                answer.entered_text.strip().lower() ==
                question.correct_answer_text.strip().lower()
            )

    elif question.question_type == "paragraph":
        # teacher review
        is_correct = None  

    new_answer = AttemptAnswer(
        attempt_id=answer.attempt_id,
        question_id=answer.question_id,
        selected_option_id=answer.selected_option_id,
        entered_text=answer.entered_text,
        is_correct=is_correct
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    return new_answer


@router.get('/answer/{attempt_id}')
def get_attempt_answers(attempt_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    answers = db.query(AttemptAnswer).filter(AttemptAnswer.attempt_id == attempt_id).all()
    return answers

@router.get('/answer/question/{question_id}')
def get_answers_by_question(question_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    answers = db.query(AttemptAnswer).filter(AttemptAnswer.question_id == question_id).all()
    return answers

@router.put('/answer/{answer_id}')
def update_attempt_answer(answer_id: int, answer: AttemptAnswerCreate, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    existing_answer = db.query(AttemptAnswer).filter(AttemptAnswer.id == answer_id).first()
    if not existing_answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    
    existing_answer.selected_option_id = answer.selected_option_id
    existing_answer.entered_text = answer.entered_text
    existing_answer.is_correct = answer.is_correct
    
    db.commit()
    db.refresh(existing_answer)
    return existing_answer

@router.delete('/answer/{answer_id}')
def delete_attempt_answer(answer_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    answer = db.query(AttemptAnswer).filter(AttemptAnswer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    db.delete(answer)
    db.commit()
    return {"detail": "Answer deleted successfully"}

@router.post('/{attempt_id}/finish')
def finish_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(404, "Attempt not found")

    test = db.query(Test).filter(Test.id == attempt.test_id).first()

    # 🌟 Duration tekshirish
    if test.duration_minutes:
        elapsed = (datetime.utcnow() - attempt.started_at).total_seconds() / 60
        if elapsed > test.duration_minutes:
            # vaqt tugagan
            pass

    # 🌟 Score hisoblash
    answers = db.query(AttemptAnswer).filter(
        AttemptAnswer.attempt_id == attempt_id
    ).all()

    correct_count = sum(1 for a in answers if a.is_correct is True)

    attempt.score = correct_count
    attempt.finished_at = datetime.utcnow()

    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "score": correct_count,
        "finished_at": attempt.finished_at
    }
