from fastapi import FastAPI, Depends, Request, HTTPException
from app.auth.auth import AuthHandler, AuthHandlerUser
from app.services.auth_service import AuthService
from app.config.settings import get_settings

# Instantiate both authentication handlers
auth_handler = AuthHandler()
auth_handler_user = AuthHandlerUser()

# Initialize FastAPI app with `auth_handler_user` as the default dependency
app = FastAPI(dependencies=[Depends(auth_handler_user)])

# Override with `auth_handler` (UUID-based) for this specific route
@app.get("/simple-endpoint", dependencies=[Depends(auth_handler)])
def simple_endpoint():
    return {"message": "This is a simple endpoint that requires UUID-based authentication"}

# All remaining routes will use `auth_handler_user` (JWT-based) by default

@app.get("/generate-org-token")
async def generate_org_token(request: Request):
    try:
        # Extract organisation_id from request state
        organisation_id = request.state.organisation_id
        org_token = AuthService.generate_org_token_flow(organisation_id)
        return {"org_token": org_token}
    except AttributeError:
        raise HTTPException(status_code=401, detail="Organisation ID not found in request state")
    except HTTPException as e:
        return {"error": e.detail}

@app.post("/another-endpoint")
def another_endpoint():
    return {"message": "This is another protected POST endpoint"}

@app.get("/protected-route")
def protected_route(request: Request):
    settings = get_settings()
    sso = settings.SSO_URL
    org = settings.ORG_LOGIN_URL
    return {"sso": sso, "org": org}

# Unauthenticated route, bypasses all auth handlers
@app.get("/", dependencies=[])
async def root():
    return {"message": "Hi, setup is done & working."}
