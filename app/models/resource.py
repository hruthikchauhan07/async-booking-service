from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # e.g., "Conference Room A"
    type = Column(String, nullable=False) # e.g., "room", "desk"
    capacity = Column(Integer, default=1)
    location = Column(String, nullable=True) # e.g., "Floor 2"
    is_active = Column(Boolean, default=True)
    
    # Relationship to Bookings
    bookings = relationship("Booking", back_populates="resource")