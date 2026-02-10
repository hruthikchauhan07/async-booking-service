from pydantic import BaseModel
from typing import Optional

# Base properties (shared)
class ResourceBase(BaseModel):
    name: str
    type: str  # e.g., "conference_room", "laptop"
    location: Optional[str] = None
    capacity: int = 1

# Properties to receive on creation
class ResourceCreate(ResourceBase):
    pass

# Properties to return to client (includes ID)
class ResourceResponse(ResourceBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True