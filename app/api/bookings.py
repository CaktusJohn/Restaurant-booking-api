from datetime import date

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.booking import EXAMPLE_BOOKING_DATE, BookingCreate, BookingList, BookingOut
from app.services.booking import cancel_booking, create_booking, get_booking, list_bookings


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать бронь",
    description="Создаёт активную бронь. Одна активная бронь на дату и время; занятый слот вернёт 409.",
    responses={
        409: {"description": "Выбранный слот уже занят", "content": {"application/json": {"example": {"detail": "Booking slot is already occupied"}}}},
        422: {"description": "Данные бронирования не прошли валидацию"},
    },
)
async def create(
    booking_data: BookingCreate = Body(
        openapi_examples={
            "standard_booking": {
                "summary": "Обычная бронь",
                "value": {
                    "name": "Анна Иванова",
                    "phone": "+79991234567",
                    "booking_date": EXAMPLE_BOOKING_DATE,
                    "booking_time": "19:00",
                    "guests": 2,
                },
            }
        }
    ),
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    return await create_booking(session, booking_data)


@router.get(
    "",
    response_model=BookingList,
    summary="Получить список бронирований",
    description="Возвращает страницу броней. Параметр date необязателен и фильтрует список по дате.",
    responses={422: {"description": "Некорректный формат даты или параметров пагинации"}},
)
async def list_all(
    session: AsyncSession = Depends(get_session),
    booking_date: date | None = Query(
        default=None,
        alias="date",
        description="Необязательный фильтр по дате в формате YYYY-MM-DD.",
        examples=[EXAMPLE_BOOKING_DATE],
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Необязательный размер страницы: от 1 до 100.",
        examples=[20],
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Необязательное число пропускаемых записей.",
        examples=[0],
    ),
) -> BookingList:
    bookings, total = await list_bookings(session, booking_date, limit, offset)
    return BookingList(items=bookings, total=total, limit=limit, offset=offset)


@router.get(
    "/{booking_id}",
    response_model=BookingOut,
    summary="Получить бронь по идентификатору",
    responses={404: {"description": "Бронь не найдена", "content": {"application/json": {"example": {"detail": "Booking not found"}}}}},
)
async def get_one(
    booking_id: int = Path(description="Идентификатор брони", examples=[1]),
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    return await get_booking(session, booking_id)


@router.delete(
    "/{booking_id}",
    response_model=BookingOut,
    summary="Отменить бронь",
    description="Не удаляет запись, а меняет её статус на cancelled. Повторная отмена вернёт 409.",
    responses={
        404: {"description": "Бронь не найдена", "content": {"application/json": {"example": {"detail": "Booking not found"}}}},
        409: {"description": "Бронь уже отменена", "content": {"application/json": {"example": {"detail": "Booking is already cancelled"}}}},
    },
)
async def cancel(
    booking_id: int = Path(description="Идентификатор брони", examples=[1]),
    session: AsyncSession = Depends(get_session),
) -> BookingOut:
    return await cancel_booking(session, booking_id)
