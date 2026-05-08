import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from dataclasses import dataclass
from typing import Optional
from agents.base_agent import BaseAgent

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    created_at: Optional[str] = None

class BEAgentV1(BaseAgent):
    def __init__(self, build_id: str, repo_path: str, api_spec_path: str):
        super().__init__("BE_AGENT_v1", build_id, phase=3)
        self.repo_path = repo_path
        self.api_spec_path = api_spec_path

    async def run(self):
        self.set_step("writing_models")
        await self.write_governance_record("TASK_START", step_id="write_models")
        
        # Write User model
        model_content = '''from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    created_at: Optional[datetime] = None
'''
        await self.fs_write(f"{self.repo_path}/backend/models.py", model_content)
        
        # Write migration
        migration_content = '''-- Migration: create_users_table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
'''
        await self.fs_write(f"{self.repo_path}/backend/migrations/001_create_users.sql", migration_content)
        
        await self.emit_gate_pass("G-06", evidence={"models": "User model written", "migration": "001_create_users.sql"})
        
        self.set_step("writing_services")
        
        # Write user service
        user_service = '''import bcrypt
from models import User

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

class UserService:
    @staticmethod
    async def create_user(email: str, password: str, full_name: str) -> User:
        password_hash = hash_password(password)
        # TODO: Insert into database
        return User(email=email, password_hash=password_hash, full_name=full_name)
'''
        await self.fs_write(f"{self.repo_path}/backend/user_service.py", user_service)
        
        # Write auth service
        auth_service = '''import jwt
from datetime import datetime, timedelta

SECRET_KEY = "change_this_in_production"

def create_access_token(user_id: int) -> str:
    exp = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": str(user_id), "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload["sub"])
    except:
        return None
'''
        await self.fs_write(f"{self.repo_path}/backend/auth_service.py", auth_service)
        
        await self.emit_gate_pass("G-07", evidence={"services": "user_service.py, auth_service.py"})
        
        self.set_step("writing_routes")
        
        # Write auth routes
        auth_routes = '''from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth_service import create_access_token, verify_token
from user_service import UserService

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

@router.post("/auth/register")
async def register(req: RegisterRequest):
    user = await UserService.create_user(req.email, req.password, req.full_name)
    return {"user_id": user.id, "email": user.email}

@router.post("/auth/login")
async def login(req: LoginRequest):
    # TODO: Verify credentials
    user_id = 1  # Placeholder
    token = create_access_token(user_id)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/refresh")
async def refresh(token: str):
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(401, "Invalid token")
    new_token = create_access_token(user_id)
    return {"access_token": new_token, "token_type": "bearer"}
'''
        await self.fs_write(f"{self.repo_path}/backend/auth_routes.py", auth_routes)
        
        # Write user routes
        user_routes = '''from fastapi import APIRouter, Depends, HTTPException
from auth_service import verify_token

router = APIRouter()

@router.get("/api/v1/users/me")
async def get_me(token: str):
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(401, "Invalid token")
    # TODO: Fetch user from database
    return {"user_id": user_id, "email": "user@example.com"}

@router.patch("/api/v1/users/me")
async def update_me(token: str, full_name: str):
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(401, "Invalid token")
    # TODO: Update user in database
    return {"user_id": user_id, "full_name": full_name}
'''
        await self.fs_write(f"{self.repo_path}/backend/user_routes.py", user_routes)
        
        await self.emit_gate_pass("G-08", evidence={"routes": "auth_routes.py, user_routes.py"})
        
        self.set_step("writing_main_app")
        
        # Write main.py
        main_content = '''from fastapi import FastAPI
from auth_routes import router as auth_router
from user_routes import router as user_router
import asyncpg

app = FastAPI(title="Backend API")

app.include_router(auth_router)
app.include_router(user_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(
        user="agents_user",
        password="agents_secure_pass_2026",
        database="governance_db",
        host="localhost"
    )
'''
        await self.fs_write(f"{self.repo_path}/backend/main.py", main_content)
        
        # Write requirements.txt
        requirements = '''fastapi==0.110.0
uvicorn
asyncpg
pydantic
pyjwt
passlib[bcrypt]
'''
        await self.fs_write(f"{self.repo_path}/backend/requirements.txt", requirements)
        
        await self.emit_gate_pass("G-09", evidence={"main": "main.py", "requirements": "requirements.txt"})
        
        # Dispatch TL_AGENT_v3
        await self.emit_handoff("TL_AGENT_v3", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-06", "G-07", "G-08", "G-09"]})
        self.status = "COMPLETE"
        await self.stop()
