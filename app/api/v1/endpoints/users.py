from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from sqlalchemy.future import select
from app.schemas.user import UserCreate, UserResponce
from typing import List
from app.core.security import get_password_hash
from app.api import deps
from app.models.user import User

router = APIRouter()

# end points

#post
@router.post("/", response_model=UserResponce)

#function -> user creation 
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):

    # check if user mail already exists?

    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # creating new user if doesn't exists already

    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        # THE FIX: Real encryption happens here
        hashed_password=get_password_hash(user_in.password),
        is_active=True, 
    )


    # adding new user to the Database

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

#get response model

@router.get("/", response_model=List[UserResponce])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


#endpoint that only works if you are logged in

@router.get("/me", response_model=UserResponce)
async def read_user_me(current_user : User = Depends(deps.get_current_user)):
    #get current user
    return current_user