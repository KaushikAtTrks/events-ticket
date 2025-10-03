from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, passes, bookings, staff, admin, validation
from app.db.mongodb import MongoDB
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect_to_database()
    print("MongoDB connected")
    yield
    await MongoDB.close_database_connection()
    print("MongoDB disconnected")


app = FastAPI(
    title="Navratri Pass Management API",
    description="API for managing Navratri event passes and bookings",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(passes.router, prefix="/passes", tags=["Passes"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(staff.router, prefix="/staff", tags=["Staff"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(validation.router, prefix="/validate", tags=["Validation"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Navratri Pass Management API",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
