from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, passes, bookings, staff, admin, validation
from app.db.mongodb import MongoDB

app = FastAPI(
    title="Navratri Pass Management API",
    description="API for managing Navratri event passes and bookings",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection events
@app.on_event("startup")
async def startup_db_client():
    await MongoDB.connect_to_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    await MongoDB.close_database_connection()

# Include routers
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
        "docs_url": "/docs"
    }
