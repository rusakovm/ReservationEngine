from fastapi import FastAPI
from app.api.resources import router as resources_router
from app.api.bookings import router as bookings_router


app = FastAPI(
    title="ReservationEngine",
    version="0.1.0",
)

app.include_router(bookings_router)
app.include_router(resources_router)


@app.get("/health")
async def health():
    return {"status": "ok"}