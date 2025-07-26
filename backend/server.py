from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import requests
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="VaultLinks API", description="Google Drive Link Management")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))

class VaultLink(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    url: str
    name: str
    access_level: str = "Restricted"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith('http'):
            raise ValueError('URL must start with http or https')
        return v
    
    @validator('access_level')
    def validate_access_level(cls, v):
        valid_levels = ["Restricted", "Anyone with link", "Public"]
        if v not in valid_levels:
            raise ValueError(f'Access level must be one of {valid_levels}')
        return v

class VaultLinkCreate(BaseModel):
    url: str
    name: str
    access_level: str = "Restricted"

class AuthRequest(BaseModel):
    session_id: str

# Authentication helper
async def get_current_user(session_token: Optional[str] = None):
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token required")
    
    # Find session in database
    session = await db.sessions.find_one({"session_token": session_token})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Check if session is expired
    if datetime.utcnow() > session.get("expires_at", datetime.utcnow()):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user = await db.users.find_one({"id": session["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

# Authentication endpoints
@api_router.post("/auth/profile")
async def authenticate_user(auth_request: AuthRequest):
    """Authenticate user with Emergent Auth session ID"""
    try:
        # Call Emergent Auth API
        headers = {"X-Session-ID": auth_request.session_id}
        response = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session ID")
        
        user_data = response.json()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data["email"]})
        
        if not existing_user:
            # Create new user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                picture=user_data.get("picture")
            )
            await db.users.insert_one(user.dict())
        else:
            user = User(**existing_user)
        
        # Create session
        session = Session(
            user_id=user.id,
            session_token=user_data["session_token"]
        )
        await db.sessions.insert_one(session.dict())
        
        return {
            "user": user,
            "session_token": session.session_token,
            "expires_at": session.expires_at
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="Authentication service unavailable")

@api_router.get("/auth/me")
async def get_current_user_info(session_token: str):
    """Get current user information"""
    user = await get_current_user(session_token)
    return user

# VaultLink endpoints
@api_router.post("/vault-links", response_model=VaultLink)
async def create_vault_link(link_data: VaultLinkCreate, session_token: str):
    """Create a new vault link"""
    user = await get_current_user(session_token)
    
    vault_link = VaultLink(
        user_id=user.id,
        url=link_data.url,
        name=link_data.name,
        access_level=link_data.access_level
    )
    
    await db.vault_links.insert_one(vault_link.dict())
    return vault_link

@api_router.get("/vault-links", response_model=List[VaultLink])
async def get_vault_links(session_token: str):
    """Get all vault links for the current user"""
    user = await get_current_user(session_token)
    
    vault_links = await db.vault_links.find({"user_id": user.id}).sort("created_at", -1).to_list(1000)
    return [VaultLink(**link) for link in vault_links]

@api_router.delete("/vault-links/{link_id}")
async def delete_vault_link(link_id: str, session_token: str):
    """Delete a vault link"""
    user = await get_current_user(session_token)
    
    # Check if link exists and belongs to user
    link = await db.vault_links.find_one({"id": link_id, "user_id": user.id})
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Delete the link
    await db.vault_links.delete_one({"id": link_id, "user_id": user.id})
    return {"message": "Link deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()