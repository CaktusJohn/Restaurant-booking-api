import re
from datetime import date, time, timedelta
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PHONE_PATTERN = re.compile(r"^(?:\+7|8)\d{10}$")
AVAILABLE_SLOTS = {time(hour) for hour in range(12, 23)}
EXAMPLE_BOOKING_DATE = (date.today() + timedelta(days=1)).isoformat()


class BookingCreate(BaseModel):
    """Данные, необходимые для создания брони."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=100,
            pattern=r"^[A-Za-zА-Яа-яЁё -]+$",
            description="Имя гостя: от 2 символов, только буквы, пробелы и дефис.",
            examples=["Анна Иванова"],
        ),
    ]
    phone: Annotated[
        str,
        Field(
            description="Номер строго в формате +7XXXXXXXXXX или 8XXXXXXXXXX.",
            examples=["+79991234567"],
        ),
    ]
    booking_date: Annotated[
        date,
        Field(description="Дата от сегодняшнего дня до 90 дней вперёд.", examples=[EXAMPLE_BOOKING_DATE]),
    ]
    booking_time: Annotated[
        time,
        Field(description="Время начала: целый час с 12:00 до 22:00.", examples=["19:00"]),
    ]
    guests: Annotated[
        int,
        Field(ge=1, le=12, strict=True, description="Количество гостей: целое число от 1 до 12.", examples=[2]),
    ]

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Номер должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX")
        return value

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, value: date) -> date:
        today = date.today()
        if not today <= value <= today + timedelta(days=90):
            raise ValueError("Дата бронирования должна быть от сегодняшнего дня до 90 дней вперёд")
        return value

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, value: time) -> time:
        if value not in AVAILABLE_SLOTS:
            raise ValueError("Доступны слоты с 12:00 до 22:00 с шагом в один час")
        return value


class BookingOut(BaseModel):
    """Бронь, сохранённая в системе."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор брони", examples=[1])
    name: str = Field(description="Имя гостя", examples=["Анна Иванова"])
    phone: str = Field(description="Телефон гостя", examples=["+79991234567"])
    booking_date: date = Field(description="Дата бронирования", examples=[EXAMPLE_BOOKING_DATE])
    booking_time: time = Field(description="Время бронирования", examples=["19:00"])
    guests: int = Field(description="Количество гостей", examples=[2])
    status: Literal["active", "cancelled"] = Field(description="Текущий статус брони", examples=["active"])


class BookingList(BaseModel):
    """Страница списка бронирований."""

    items: list[BookingOut] = Field(description="Брони на запрошенной странице")
    total: int = Field(description="Общее число броней с учётом фильтра")
    limit: int = Field(description="Использованный размер страницы")
    offset: int = Field(description="Использованное смещение")
