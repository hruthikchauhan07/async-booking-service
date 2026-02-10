from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import users, login, resources, bookings         # <- importing login, resources, user
from app.models import user, resource, booking


app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(login.router, prefix="/api/v1", tags=["login"])
app.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["bookings"])


@app.get("/")
def read_root():
    return {"status":"Dark Passanger has awake ~_~"}