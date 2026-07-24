from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="master")  # "admin" или "master"
    base_address = Column(String, nullable=True)

    orders = relationship("Order", back_populates="master")
    hotel_bookings = relationship("HotelBooking", back_populates="master")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    client_name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    status = Column(String, default="new")  # "new", "in_progress", "completed"

    master_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    master = relationship("User", back_populates="orders")

class HotelBooking(Base):
    __tablename__ = "hotel_bookings"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("users.id"))
    hotel_name = Column(String)
    city_or_address = Column(String)
    check_in = Column(String)
    check_out = Column(String)
    price = Column(Float)

    master = relationship("User", back_populates="hotel_bookings")