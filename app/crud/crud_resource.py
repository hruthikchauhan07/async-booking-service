from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.models.resource import Resource
from app.models.booking import Booking  # <--- Critical Import
from app.schemas.resource import ResourceCreate

async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Resource).offset(skip).limit(limit))
    return result.scalars().all()

async def create_resource(db: AsyncSession, obj_in: ResourceCreate):
    db_obj = Resource(
        name=obj_in.name,
        type=obj_in.type,
        location=obj_in.location,
        capacity=obj_in.capacity,
        is_active=True
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_available(
    db: AsyncSession, 
    start_time: datetime, 
    end_time: datetime, 
    min_capacity: int
):
    """
    Finds resources that are NOT booked during the requested time slot.
    """
    # 1. FIND BUSY RESOURCES
    # Select IDs of resources that have a confirmed booking overlapping our time
    # Overlap Logic: (ExistingStart < RequestedEnd) AND (ExistingEnd > RequestedStart)
    busy_subquery = select(Booking.resource_id).where(
        and_(
            Booking.status == "confirmed",
            and_(
                Booking.start_time < end_time,
                Booking.end_time > start_time
            )
        )
    )

    # 2. FIND FREE RESOURCES
    # Select Resources whose ID is NOT in the busy list
    query = select(Resource).where(
        and_(
            Resource.id.not_in(busy_subquery),
            Resource.capacity >= min_capacity,
            Resource.is_active == True
        )
    )
    
    result = await db.execute(query)
    return result.scalars().all()