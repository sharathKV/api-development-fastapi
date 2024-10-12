from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, Any
from typing_extensions import Annotated

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
class UserOut(BaseModel):
    id: int
    email: EmailStr
    create_at: datetime
    
    class Config:
        orm_mode = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    create_at: datetime
    owner_id: int
    owner: UserOut
    
    class Config:
        orm_mode = True

class PostsWithVotes(BaseModel):
    Post: PostResponse
    votes: int
    
    class Config:
        orm_mode = True
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    
class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(strict=True, le=1)]