from fastapi import FastAPI
from auth.auth import router as auth_router
from routes.test import router as test_router
from routes.question import router as question_router
from routes.option import router as option_router
from routes.attempt import router as attempt_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(test_router)
app.include_router(question_router)
app.include_router(option_router)
app.include_router(attempt_router)

@app.get('/')
def root():
    return {"message":"Server is live!"}
