from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.models.booking import Booking
from app.schemas.booking import BookingCreate

async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Booking).offset(skip).limit(limit))
    return result.scalars().all()

async def create_booking(db: AsyncSession, obj_in: BookingCreate, user_id: int):
    # 1. CHECK FOR CONFLICTS (The most important part)
    # Is there any existing booking for this room that overlaps with the requested time?
    # Logic: (StartA < EndB) AND (EndA > StartB)
    query = select(Booking).where(
        and_(
            Booking.resource_id == obj_in.resource_id,
            Booking.status == "confirmed", # Only check active bookings
            and_(
                Booking.start_time < obj_in.end_time,
                Booking.end_time > obj_in.start_time
            )
        )
    )
    result = await db.execute(query)
    conflict = result.scalar_one_or_none()

    if conflict:
        return None # Room is taken!

    # 2. CREATE BOOKING
    db_obj = Booking(
        user_id=user_id,
        resource_id=obj_in.resource_id,
        start_time=obj_in.start_time,
        end_time=obj_in.end_time,
        status="confirmed"
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

    # Deleting the Booking

async def delete_booking(db: AsyncSession, booking_id: int):
    # 1. Find the booking
    query = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(query)
    booking = result.scalar_one_or_none()
    
    if booking:
        await db.delete(booking)
        await db.commit()
    return booking

async def get_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    """
    Get bookings for a specific user only.
    """
    query = select(Booking).where(Booking.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()