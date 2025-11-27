"""Authentication API endpoints"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from app.services.auth_service import AuthService
from app.clients.database_client import get_db
from app.dependencies.auth import get_current_user
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to create AuthService"""
    return AuthService(db)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user with email and password
    
    Request body:
    {
        "email": "krishna@example.com",
        "password": "SecurePass123!",
        "display_name": "Krishna Yadav"  (optional)
    }
    
    Response:
    {
        "access_token": "eyJ...",
        "refresh_token": "abc123...",
        "token_type": "bearer",
        "user": {
            "id": "uuid",
            "email": "krishna@example.com",
            "display_name": "Krishna Yadav"
        }
    }
    """
    try:
        auth_service = AuthService(db)
        
        # Register user (email will be lowercased in service)
        user = await auth_service.register_user(
            email=request.email,
            password=request.password,
            display_name=request.display_name
        )
        
        # Generate tokens
        tokens = await auth_service.create_tokens(user.id)
        
        # Update last login
        await auth_service.update_last_login(user.id)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                display_name=user.display_name
            )
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user with email and password
    
    Request body:
    {
        "email": "krishna@example.com",
        "password": "SecurePass123!"
    }
    
    Response: Same as /register
    """
    try:
        auth_service = AuthService(db)
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            email=request.email,
            password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Generate tokens
        tokens = await auth_service.create_tokens(user.id)
        
        # Update last login
        await auth_service.update_last_login(user.id)
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                display_name=user.display_name
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information (requires authentication)
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
    {
        "id": "uuid",
        "email": "krishna@example.com",
        "display_name": "Krishna Yadav"
    }
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name
    )


@router.post("/logout")
async def logout(
    user_id: str = Depends(get_current_user)
):
    """
    Logout user (requires authentication)
    
    In a full implementation, this would revoke the refresh token.
    For now, it's a placeholder - frontend will delete tokens from localStorage.
    """
    logger.info(f"User logged out: {user_id}")
    return {"message": "Successfully logged out"}

