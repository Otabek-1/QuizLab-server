from pydantic import BaseModel
from typing import Optional

class AttemptCreate(BaseModel):
    test_id:int
    user_id:int
    started_at:Optional[str] = None
    finished_at:Optional[str] = None
    score:int

class AttemptAnswerCreate(BaseModel):
    attempt_id: int
    question_id: int
    selected_option_id: Optional[int] = None
    entered_text: Optional[str] = None
    is_correct: bool