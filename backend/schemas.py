from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# --- Схемы Авторизации ---
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    role: str
    company_id: Optional[UUID]

    class Config:
        from_attributes = True

# --- Схемы Заказов ---
class OrderBase(BaseModel):
    title: str
    description: Optional[str] = None
    address: Optional[str] = None

class OrderCreate(OrderBase):
    assigned_to: Optional[UUID] = None

class OrderStatusUpdate(BaseModel):
    status: str

class OrderResponse(OrderBase):
    id: UUID
    status: str
    company_id: UUID
    assigned_to: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Схемы Геолокации ---
class GeoLocation(BaseModel):
    latitude: float
    longitude: float
    timestamp: str

# --- Схемы Склада (Van Stock - Pro Tier) ---
class InventoryItemBase(BaseModel):
    sku: str
    name: str
    unit_price: float

class InventoryItemResponse(InventoryItemBase):
    id: UUID

    class Config:
        from_attributes = True

class VanStockConsume(BaseModel):
    item_id: UUID
    quantity: int
    order_id: UUID

class VanInventoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    item_id: UUID
    quantity: int
    item: Optional[InventoryItemResponse] = None

    class Config:
        from_attributes = True