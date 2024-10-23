from fastapi import FastAPI, Depends, Request, HTTPException
from app.auth.auth import AuthHandler
from app.services.auth_service import AuthService
from app.config.settings import get_settings

# app = FastAPI()

# Instantiate the AuthHandler to use in the API routes
auth_handler = AuthHandler()

app = FastAPI(dependencies=[Depends(auth_handler)])  # Apply authentication globally

# Define API endpoints without explicitly passing `current_user`

@app.get("/generate-org-token")
async def generate_org_token(request: Request):
    try:
        # Step 1: Extract organisation_id from request state
        try:
            organisation_id = request.state.organisation_id
        except AttributeError:
            raise HTTPException(status_code=401, detail="organisation ID not found in request state")

        # Step 2: Call the function that encapsulates the entire token generation flow
        org_token = AuthService.generate_org_token_flow(organisation_id)
        return {"org_token": org_token}
    except HTTPException as e:
        return {"error": e.detail}

@app.get("/simple-endpoint")
def simple_endpoint():
    return {"message": "This is a simple endpoint that requires authentication"}

@app.post("/another-endpoint")
def another_endpoint():
    return {"message": "This is another protected POST endpoint"}

@app.get("/protected-route")
def protected_route(request: Request):
    # Access user_id and organisation_id from the request
    user_id = request.state.user_id
    organisation_id = request.state.organisation_id
    settings = get_settings()
    sso=settings.SSO_URL
    org=settings.ORG_LOGIN_URL

    return {"user_id": user_id, "organisation_id": organisation_id, "sso ":sso, "org": org}

@app.get("/")
async def root():
    return {"message": "Hi, setrup is done & working."}