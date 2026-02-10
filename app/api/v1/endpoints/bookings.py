from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.crud import crud_booking
from app.api import deps
from app.models.user import User
from sqlalchemy import select
from app.models.booking import Booking

router = APIRouter()

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new booking. Fails if the slot is taken.
    """
    # 1. Validate Logic (Start < End)
    if booking_in.start_time >= booking_in.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    # 2. Attempt to Book
    booking = await crud_booking.create_booking(db=db, obj_in=booking_in, user_id=current_user.id)
    
    if not booking:
        raise HTTPException(status_code=409, detail="Resource is already booked for this time slot")
        
    return booking

@router.get("/", response_model=List[BookingResponse])
async def read_bookings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieve bookings.
    - Superusers: See ALL bookings.
    - Regular Users: See only THEIR OWN bookings.
    """
    if current_user.is_superuser:
        # Admin sees everything
        return await crud_booking.get_multi(db, skip=skip, limit=limit)
    else:
        # User sees only their own stuff
        return await crud_booking.get_by_user(
            db=db, 
            user_id=current_user.id, 
            skip=skip, 
            limit=limit
        )
    
#endpoint to delete a booking

@router.delete("/{booking_id}", response_model=BookingResponse)
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Cancel a booking.
    """
    # 1. Find the booking
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # 2. SECURITY CHECK: Am I the owner? (Or a Superuser?)
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    # 3. Delete
    await db.delete(booking)
    await db.commit()
    
    return booking


