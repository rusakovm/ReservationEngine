
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas.resource import (
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)
from app.db.database import get_db
from app.db.models import Resource


router = APIRouter(
    prefix="/resources",
    tags=["Resources"],
)


# Получить список активных ресурсов
@router.get("/", response_model=list[ResourceResponse])
def get_resources(db: Session = Depends(get_db)):
    statement = select(Resource).where(
        Resource.is_active.is_(True)
    )

    resources = db.scalars(statement).all()

    return resources


# Создать ресурс
@router.post("/", response_model=ResourceResponse, status_code=201)
def create_resource(
    data: ResourceCreate,
    db: Session = Depends(get_db)
):
    resource = Resource(**data.model_dump())

    db.add(resource)
    db.commit()
    db.refresh(resource)

    return resource


# Получить ресурс по ID
@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    statement = select(Resource).where(
        Resource.id == resource_id,
        Resource.is_active.is_(True)
    )

    resource = db.scalars(statement).first()

    if resource is None:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    return resource


# Деактивировать ресурс
@router.delete("/{resource_id}", response_model=ResourceResponse)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    statement = select(Resource).where(
        Resource.id == resource_id,
        Resource.is_active.is_(True)
    )

    resource = db.scalars(statement).first()

    if resource is None:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    resource.is_active = False

    db.commit()
    db.refresh(resource)

    return resource


# Частично изменить ресурс
@router.patch("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: Session = Depends(get_db)
):
    statement = select(Resource).where(
        Resource.id == resource_id,
        Resource.is_active.is_(True)
    )

    resource = db.scalars(statement).first()

    if resource is None:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    changes = data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    for field, value in changes.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)

    return resource
