from httpx import AsyncClient


async def test_create_booking(client: AsyncClient, booking_payload: dict[str, str | int]) -> None:
    response = await client.post("/bookings", json=booking_payload)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        **booking_payload,
        "booking_time": "19:00:00",
        "status": "active",
    }


async def test_create_booking_rejects_invalid_phone(
    client: AsyncClient, booking_payload: dict[str, str | int]
) -> None:
    response = await client.post("/bookings", json={**booking_payload, "phone": "79991234567"})

    assert response.status_code == 422


async def test_create_booking_rejects_invalid_time(
    client: AsyncClient, booking_payload: dict[str, str | int]
) -> None:
    response = await client.post("/bookings", json={**booking_payload, "booking_time": "12:30"})

    assert response.status_code == 422


async def test_create_booking_rejects_invalid_guest_count(
    client: AsyncClient, booking_payload: dict[str, str | int]
) -> None:
    response = await client.post("/bookings", json={**booking_payload, "guests": 13})

    assert response.status_code == 422


async def test_booking_lifecycle(client: AsyncClient, booking_payload: dict[str, str | int]) -> None:
    created = await client.post("/bookings", json=booking_payload)
    booking_id = created.json()["id"]

    conflict = await client.post("/bookings", json=booking_payload)
    listed = await client.get("/bookings", params={"date": booking_payload["booking_date"]})
    cancelled = await client.delete(f"/bookings/{booking_id}")
    repeated_cancel = await client.delete(f"/bookings/{booking_id}")
    missing = await client.get("/bookings/999")

    assert conflict.status_code == 409
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert cancelled.json()["status"] == "cancelled"
    assert repeated_cancel.status_code == 409
    assert missing.status_code == 404
