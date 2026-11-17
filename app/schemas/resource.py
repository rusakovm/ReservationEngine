from pydantic import BaseModel, Field


class ResourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    resource_type: str
    description: str = ""


class ResourceResponse(ResourceCreate):
    id: int
    is_active: bool

class ResourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    resource_type: str | None = None
    description: str | None = None
