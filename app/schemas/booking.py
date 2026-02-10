from datetime import datetime
from pydantic import BaseModel, FutureDatetime

# Base properties
class BookingBase(BaseModel):
    resource_id: int
    start_time: FutureDatetime # Must be in the future
    end_time: FutureDatetime

# Properties to receive on creation
class BookingCreate(BookingBase):
    pass

# Properties to return to client (includes ID and Status)
class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True