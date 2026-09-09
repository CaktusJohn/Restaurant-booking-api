import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.booking import BookingCreate
from app.services.booking import cancel_booking, create_booking


async def test_service_rejects_occupied_slot(
    session: AsyncSession, booking_payload: dict[str, str | int]
) -> None:
    booking_data = BookingCreate.model_validate(booking_payload)
    await create_booking(session, booking_data)

    with pytest.raises(HTTPException) as exception:
        await create_booking(session, booking_data)

    assert exception.value.status_code == 409


async def test_service_rejects_repeated_cancellation(
    session: AsyncSession, booking_payload: dict[str, str | int]
) -> None:
    booking = await create_booking(session, BookingCreate.model_validate(booking_payload))
    await cancel_booking(session, booking.id)

    with pytest.raises(HTTPException) as exception:
        await cancel_booking(session, booking.id)

    assert exception.value.status_code == 409
