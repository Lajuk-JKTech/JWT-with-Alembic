from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config.settings import Settings

settings = Settings()

class AuthHandler:
    def __init__(self):
        self.security = HTTPBearer()  # Uses Bearer token authentication
        self.JWT_PUBLIC = settings.JWT_PUBLIC
        self.API_KEY = settings.API_KEY  # Get the API_KEY from settings

    def decode_jwt(self, token: str):
        try:
            # Decode the token
            payload = jwt.decode(token, self.JWT_PUBLIC, algorithms=["RS256"])

            # Extract API key from the payload
            api_key = payload.get("api_key")

            # Check if API key is present in the payload
            if api_key is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key missing in JWT payload"
                )

            # Check if the api_key matches the one in settings
            if api_key != self.API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )

            # Return a success flag or other data if needed
            return True

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature"
            )
        except jwt.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token could not be decoded"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )

    def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        # Decode JWT token and validate api_key
        token = credentials.credentials
        self.decode_jwt(token)

        # Optionally set a success flag or other data in request state if needed
        request.state.is_authenticated = True