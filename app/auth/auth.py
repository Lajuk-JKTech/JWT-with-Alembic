from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config.settings import Settings
import uuid

settings = Settings()

class AuthHandler:
    def __init__(self):
        self.security = HTTPBearer()  # Uses Bearer token authentication
        self.API_KEY = settings.API_KEY  # Get the API_KEY from settings

    def validate_uuid(self, token: str):
        try:
            # Validate if the token is a UUID
            token_uuid = uuid.UUID(token)

            # Check if the UUID matches the API key
            if str(token_uuid) != self.API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )

            # Return success flag or other data if needed
            return True

        except ValueError:
            # Raised if the token is not a valid UUID format
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid UUID format"
            )

    def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        # Validate the UUID token against the API key
        token = credentials.credentials
        self.validate_uuid(token)

class AuthHandlerUser:
    def __init__(self):
        self.security = HTTPBearer()  # Uses Bearer token authentication
        self.JWT_PUBLIC = settings.JWT_PUBLIC

    def decode_jwt(self, token: str):
        try:
            # Decode the token
            payload = jwt.decode(token, self.JWT_PUBLIC, algorithms=["RS256"])

            # Extract user ID and organisation ID from the payload
            user_id = payload.get("id")
            organisation_id = payload.get("scope", {}).get("x-inveniam-organisationId")

            if user_id is None or organisation_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid JWT payload"
                )

            # Return both user_id and organisation_id
            return user_id, organisation_id
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

        if request.url.path == "/simple-endpoint":
            # Skip JWT decoding for this endpoint
            return
        
        # Decode JWT token
        token = credentials.credentials
        user_id, organisation_id = self.decode_jwt(token)

        # Set user_id and organisation_id in the request state
        request.state.user_id = user_id
        request.state.organisation_id = organisation_id
