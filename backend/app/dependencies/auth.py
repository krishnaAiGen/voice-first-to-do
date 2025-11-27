"""Authentication dependencies for FastAPI"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.auth import verify_token
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# HTTP Bearer token security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency to extract and verify current user from JWT token
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}
    
    Args:
        credentials: HTTP Authorization header with Bearer token
    
    Returns:
        user_id string if token is valid
    
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> str | None:
    """
    Optional authentication - returns user_id if authenticated, None otherwise
    
    Usage in routes where auth is optional:
        @router.get("/public-or-private")
        async def route(user_id: str | None = Depends(get_optional_user)):
            if user_id:
                return {"message": f"Hello user {user_id}"}
            return {"message": "Hello anonymous"}
    
    Args:
        credentials: HTTP Authorization header (optional)
    
    Returns:
        user_id string if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return verify_token(token)

