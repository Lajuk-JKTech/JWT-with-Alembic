from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.auth.auth import AuthHandler
from app.config.database import get_session
from app.models.user import VM_Users

# app = FastAPI()

# Instantiate the AuthHandler to use in the API routes
auth_handler = AuthHandler()

app = FastAPI(dependencies=[Depends(auth_handler)])  # Apply authentication globally

# Define API endpoints without explicitly passing `current_user`

@app.get("/simple-endpoint")
def simple_endpoint():
    return {"message": "This is a simple endpoint that requires authentication"}

@app.post("/another-endpoint")
def another_endpoint():
    return {"message": "This is another protected POST endpoint"}

@app.get("/protected-route")
def protected_route(
    current_user: VM_Users = Depends(auth_handler),
    db: Session = Depends(get_session)
):
    return {"message": f"Hello {current_user.first_name}, your token is valid!"}

@app.get("/")
async def root():
    return {"message": "Hi, setrup is done & working."}