from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config.settings import Settings

settings = Settings()

class AuthHandler:
    def __init__(self):
        self.security = HTTPBearer()  # Uses Bearer token authentication
        self.JWT_PUBLIC = settings.JWT_PUBLIC

    def decode_jwt(self, token: str):
        try:
            # Decode the token
            payload = jwt.decode(token, self.JWT_PUBLIC, algorithms=["RS256"])

            # Extract user ID and organization ID from the payload
            user_id = payload.get("id")
            organization_id = payload.get("scope", {}).get("x-inveniam-organisationId")

            if user_id is None or organization_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid JWT payload"
                )

            # Return both user_id and organization_id
            return user_id, organization_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )

    def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        # Decode JWT token
        token = credentials.credentials
        user_id, organization_id = self.decode_jwt(token)

        # Set user_id and organization_id in the request state
        request.state.user_id = user_id
        request.state.organization_id = organization_id
