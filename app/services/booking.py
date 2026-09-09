from datetime import date, time

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.schemas.booking import BookingCreate


async def create_booking(session: AsyncSession, data: BookingCreate) -> Booking:
    occupied_slot = await session.scalar(
        select(Booking.id).where(
            Booking.booking_date == data.booking_date,
            Booking.booking_time == data.booking_time,
            Booking.status == "active",
        )
    )
    if occupied_slot is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking slot is already occupied")

    booking = Booking(**data.model_dump())
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


async def get_booking(session: AsyncSession, booking_id: int) -> Booking:
    booking = await session.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


async def list_bookings(
    session: AsyncSession, booking_date: date | None, limit: int, offset: int
) -> tuple[list[Booking], int]:
    filters = [Booking.booking_date == booking_date] if booking_date else []
    total = await session.scalar(select(func.count()).select_from(Booking).where(*filters))
    bookings = await session.scalars(
        select(Booking).where(*filters).order_by(Booking.booking_date, Booking.booking_time, Booking.id).limit(limit).offset(offset)
    )
    return list(bookings), total or 0


async def cancel_booking(session: AsyncSession, booking_id: int) -> Booking:
    booking = await get_booking(session, booking_id)
    if booking.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking is already cancelled")

    booking.status = "cancelled"
    await session.commit()
    await session.refresh(booking)
    return booking
