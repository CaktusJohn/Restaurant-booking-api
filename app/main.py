from fastapi import FastAPI

from app.api.bookings import router as bookings_router


app = FastAPI(
    title="Restaurant Booking API",
    description="API для создания, просмотра и отмены бронирований в ресторане.",
    version="1.0.0",
)
app.include_router(bookings_router)
