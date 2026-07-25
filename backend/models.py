import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base

# 1. Таблица компаний и подписок (Feature Flags)
class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="starter")  # 'starter', 'pro', 'enterprise'
    feature_flags = Column(JSONB, default={
        "ocr": False,
        "van_stock": False,
        "ai_quality": False,
        "voice": False
    })
    created_at = Column(DateTime, server_default=func.now())

# 2. Пользователи (Сотрудники / Выездные мастера)
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="technician")
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# 3. Заказы / Задачи
class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    address = Column(String(500), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    created_at = Column(DateTime, server_default=func.now())

# 4. Склад в машине (Van Stock)
class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(180), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    unit_price = Column(Numeric(10, 2))

class VanInventory(Base):
    __tablename__ = "van_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"))
    quantity = Column(Integer, default=0)

# 5. Инвойсы и финансовые акты
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    status = Column(String(50), default="draft")
    pdf_url = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())