from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


#this is the engine

engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo = True, future = True)

#session making

AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False,
    autoflush = False,
)

#injecting dependency 
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()