import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_session
from app.models.user import VM_Users
from app.config.settings import Settings

settings = Settings()

# Use FastAPI's HTTPBearer scheme to get the token from the Authorization header
class AuthHandler:
    def __init__(self):
        self.security = HTTPBearer()  # Uses Bearer token authentication
        self.secret_key = settings.SECRET_KEY

    def decode_jwt(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["RS256"])
            user_id = payload.get("id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid JWT payload"
                )
            return user_id
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

    def verify_user(self, user_id: str, db: Session):
        user = db.query(VM_Users).filter(VM_Users.aggregateid == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_session)):
        # Decode JWT token
        token = credentials.credentials
        user_id = self.decode_jwt(token)

        # Verify user exists in the database
        return self.verify_user(user_id, db)
