from pydantic import BaseModel

class User(BaseModel):
    tg_id: int
    username: str

class Login(BaseModel):
    tg_id: int