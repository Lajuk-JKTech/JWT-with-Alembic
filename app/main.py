from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.auth.auth import AuthHandler
from app.config.database import get_session
from app.models.user import VM_Users

app = FastAPI()

# Instantiate the AuthHandler to use in the API routes
auth_handler = AuthHandler()

@app.get("/protected-route")
def protected_route(
    current_user: VM_Users = Depends(auth_handler),
    db: Session = Depends(get_session)
):
    return {"message": f"Hello {current_user.first_name}, your token is valid!"}

@app.get("/")
async def root():
    return {"message": "Hi, setrup is done & working."}