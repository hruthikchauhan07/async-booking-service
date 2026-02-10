from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.resource import ResourceCreate, ResourceResponse
from app.crud import crud_resource
from app.api import deps
from app.models.user import User

router = APIRouter()

# --- 1. SEARCH ENDPOINT (New) ---
@router.get("/search", response_model=List[ResourceResponse])
async def search_resources(
    start_time: datetime,
    end_time: datetime,
    min_capacity: int = 1,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Find available resources for a specific time slot.
    Example: ?start_time=2026-02-15T10:00:00Z&end_time=2026-02-15T11:00:00Z
    """
    if start_time >= end_time:
         raise HTTPException(status_code=400, detail="Start time must be before end time")
         
    resources = await crud_resource.get_available(
        db=db, 
        start_time=start_time, 
        end_time=end_time, 
        min_capacity=min_capacity
    )
    return resources

# --- 2. LIST ALL ENDPOINT ---
@router.get("/", response_model=List[ResourceResponse])
async def read_resources(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieve all resources.
    """
    return await crud_resource.get_multi(db, skip=skip, limit=limit)

# --- 3. CREATE ENDPOINT ---
@router.post("/", response_model=ResourceResponse)
async def create_resource(
    resource_in: ResourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new resource.
    """
    return await crud_resource.create_resource(db=db, obj_in=resource_in)