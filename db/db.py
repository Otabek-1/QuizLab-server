from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

engine = create_engine("postgresql://postgres.hcyiadrfsyulxhuodcrk:Ibr0him$!@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String(20))
    username = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tests = relationship("Test", back_populates="creator")

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    description = Column(String(150), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    duration_minutes = Column(Integer, nullable=True)  # yangi
    max_attempts = Column(Integer, nullable=True)      # yangi

    creator = relationship("User", back_populates="tests")
    questions = relationship("Question", back_populates="test")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    text = Column(String(255))
    image_url = Column(String(255), nullable=True)

    question_type = Column(String(30), default="single_choice")  # yangi

    # short_answer uchun optional to‘g‘ri javob
    correct_answer_text = Column(String(255), nullable=True)      # yangi

    test = relationship("Test", back_populates="questions")
    options = relationship("Option", back_populates="question")


class Option(Base):
    __tablename__ = "options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    text = Column(String(255))
    is_correct = Column(Boolean, default=False)
    
    question = relationship("Question", back_populates="options")

class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime)
    finished_at = Column(DateTime, nullable=True)
    score = Column(Integer)
    
    user = relationship("User")
    test = relationship("Test")

class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)
    # short/paragraph answerlar uchun:
    entered_text = Column(String(255), nullable=True)  # yangi
    is_correct = Column(Boolean)
    attempt = relationship("Attempt")
    question = relationship("Question")
    selected_option = relationship("Option")


# Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()