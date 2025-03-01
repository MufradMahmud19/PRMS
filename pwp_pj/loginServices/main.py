"""
User Management API using FastAPI and Redis.

Endpoints:
1. User Sign Up       - POST /auth/signup
2. User Login         - POST /auth/login
3. Refresh Token      - POST /auth/refresh
4. Logout            - POST /auth/logout
5. Validate Token    - POST /auth/validate
6. Get User Details  - GET /auth/user/{user_id}
7. Delete User       - DELETE /auth/user/{user_id}
8. Update User Info  - PUT /auth/user/{user_id}

Author: Noman
Date: March 1, 2025
"""

import time
import hashlib
from typing import Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis_om import get_redis_connection, HashModel, Field
import jwt

# FastAPI app initialization
app = FastAPI(debug=True)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# Redis connection
redis = get_redis_connection(
    host='redis-13980.c339.eu-west-3-1.ec2.redns.redis-cloud.com',
    port=13980,
    password='A9EAM68RA1HgkYsP4jxFQctXE5ZRuaiP',
    decode_responses=True
)

# Secret key for JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(HashModel):
    """User model stored in Redis."""
    username: str = Field(index=True)
    email: str
    hashed_password: str
    created_at: str = time.strftime("%Y-%m-%d %H:%M:%S")

    # pylint: disable=too-few-public-methods
    class Meta:
        """Meta class for Redis storage."""
        database = redis


# pylint: disable=too-few-public-methods
class SignupRequest(BaseModel):
    """Request model for user signup."""
    username: str
    email: str
    password: str

# pylint: disable=too-few-public-methods
class LoginRequest(BaseModel):
    """Request model for user login."""
    username: str
    password: str

# pylint: disable=too-few-public-methods
class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    token_type: str

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/auth/signup")
def signup(user: SignupRequest):
    """Registers a new user."""
    if User.find(User.username == user.username).all():
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    new_user.save()

    return {"message": "User registered successfully"}

@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    """Authenticates a user and returns an access token."""
    users = User.find(User.username == credentials.username).all()
    if not users or users[0].hashed_password != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": credentials.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/validate")
def validate_token(token: str):
    """Validates the access token and extracts user details."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return {"username": username}
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

@app.get("/auth/user/{user_id}")
def get_user(user_id: str):
    """Retrieves user details by ID."""
    user = User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/auth/user/{user_id}")
def delete_user(user_id: str):
    """Deletes a user."""
    try:
        User.delete(user_id)
        return {"message": "User deleted successfully"}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc

@app.put("/auth/user/{user_id}")
def update_user(user_id: str, user_data: SignupRequest):
    """Updates user information."""
    user = User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = user_data.username
    user.email = user_data.email
    user.hashed_password = hash_password(user_data.password)
    user.save()

    return {"message": "User updated successfully"}
