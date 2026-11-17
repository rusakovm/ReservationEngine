from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.schemas.booking import BookingUpdateTime
from app.schemas.booking import BookingCreate, BookingResponse
from app.db.database import get_db
from app.db.models import Resource, Booking


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db)
):
    resource = db.scalars(
        select(Resource)
        .where(Resource.id == data.resource_id)
        .with_for_update()
    ).first()

    if resource is None or not resource.is_active:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    statement = select(Booking).where(
        Booking.resource_id == data.resource_id,
        Booking.status == "active",
        Booking.start_time < data.end_time,
        Booking.end_time > data.start_time
    )

    existing_booking = db.scalars(statement).first()

    if existing_booking is not None:
        raise HTTPException(
            status_code=409,
            detail="Resource is already booked"
        )

   

    booking = Booking(**data.model_dump())

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking

@router.get("/", response_model=list[BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    statement = select(Booking)

    bookings = db.scalars(statement).all()

    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    statement = select(Booking).where(
        Booking.id == booking_id
    )

    booking = db.scalars(statement).first()

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking
@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    statement = select(Booking).where(
        Booking.id == booking_id
    )

    booking = db.scalars(statement).first()

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Booking already cancelled"
        )

    booking.status = "cancelled"

    db.commit()
    db.refresh(booking)

    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    data: BookingUpdateTime,
    db: Session = Depends(get_db)
):

    booking = db.get(Booking, booking_id)

    # Сначала проверяем бронирование
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Затем блокируем ресурс
    resource = db.scalars(
        select(Resource)
        .where(Resource.id == booking.resource_id)
        .with_for_update()
    ).first()

    if resource is None or not resource.is_active:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    # Повторно загружаем актуальное состояние бронирования
    db.refresh(booking)

    if booking.status != "active":
        raise HTTPException(
            status_code=409,
            detail="Cannot update cancelled booking"
        )
   
    new_start = (
        data.start_time
        if data.start_time is not None
        else booking.start_time
    )

    new_end = (
        data.end_time
        if data.end_time is not None
        else booking.end_time
    )

    if new_start.tzinfo is None or new_end.tzinfo is None:
        raise HTTPException(
            status_code=422,
            detail="Timezone is required"
        )

    if new_end <= new_start:
        raise HTTPException(
            status_code=422,
            detail="End time must be after start time"
        )

    statement = select(Booking).where(
        Booking.resource_id == booking.resource_id,
        Booking.id != booking_id,
        Booking.status == "active",
        Booking.start_time < new_end,
        Booking.end_time > new_start
    )

    existing_booking = db.scalars(statement).first()

    if existing_booking is not None:
        raise HTTPException(
            status_code=409,
            detail="Time slot is already booked"
        )

    booking.start_time = new_start
    booking.end_time = new_end

    db.commit()
    db.refresh(booking)

    return booking