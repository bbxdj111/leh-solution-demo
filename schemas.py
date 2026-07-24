from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "master"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class OrderCreate(BaseModel):
    client_name: str
    title: str
    description: str
    image_url: Optional[str] = None  # <-- Опциональная ссылка на фото

class OrderStatusUpdate(BaseModel):
    status: str

class OrderResponse(BaseModel):
    id: int
    client_name: str
    title: str
    description: str
    status: str
    ai_analysis: Optional[str] = None
    image_url: Optional[str] = None  # <-- Возвращаем ссылку на фото

    class Config:
        from_attributes = True