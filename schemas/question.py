from pydantic import BaseModel
from typing import Optional

class QuestionCreate(BaseModel):
    test_id:int
    text:str
    image_url: Optional[str] = None
    question_type: Optional[str] = "single_choice"
    correct_answer_text: Optional[str] = None