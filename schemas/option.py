from pydantic import BaseModel

class OptionCreate(BaseModel):
    question_id:int
    text:str
    is_correct:bool = False