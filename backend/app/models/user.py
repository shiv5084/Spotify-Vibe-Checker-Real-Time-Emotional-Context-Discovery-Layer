from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

class Profile(BaseModel):
    id: UUID = Field(..., description="Unique profile identifier, matching Supabase auth user ID")
    email: EmailStr = Field(..., description="User email address")
    display_name: Optional[str] = Field(None, description="Display name for the user")
    avatar_url: Optional[str] = Field(None, description="URL of user avatar image")
    prompts_used: int = Field(0, description="Total number of prompts executed by the user")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserSession(BaseModel):
    user_id: UUID
    email: EmailStr
    token: str
