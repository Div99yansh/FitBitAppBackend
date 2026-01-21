from fastapi import APIRouter, HTTPException, status, Depends
import logging
from sqlalchemy.orm import Session
import uuid

from database import get_db, UserDB
from schemas.auth_schemas import LoginRequest, SignupRequest, AuthUser, AuthResponse
from auth.security import verify_password, get_password_hash, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user and return JWT token"""
    try:
        # Check if user already exists
        existing_user = db.query(UserDB).filter(UserDB.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user with hashed password
        new_user = UserDB(
            id=str(uuid.uuid4()),
            name=request.name,
            email=request.email,
            age=request.age,
            password_hash=get_password_hash(request.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create access token
        token = create_access_token(data={"sub": new_user.id})

        logger.info(f"New user registered: {new_user.email}")

        return AuthResponse(
            user=AuthUser(
                id=new_user.id,
                email=new_user.email,
                name=new_user.name,
                age=new_user.age
            ),
            token=token,
            message="User registered successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password",
    description="Authenticate user and return JWT token"
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    try:
        # Find user by email
        user = db.query(UserDB).filter(UserDB.email == request.email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if user has a password set
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create access token
        token = create_access_token(data={"sub": user.id})

        logger.info(f"User logged in: {user.email}")

        return AuthResponse(
            user=AuthUser(
                id=user.id,
                email=user.email,
                name=user.name,
                age=user.age
            ),
            token=token,
            message="Login successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )
