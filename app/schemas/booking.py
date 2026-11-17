from pydantic import BaseModel, Field
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

class BookingCreate(BaseModel):
    resource_id: int = Field(gt=0)
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_booking(self):
        if self.start_time.tzinfo is None or self.end_time.tzinfo is None:
            raise ValueError("Timezone is required")

        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

        return self


class BookingResponse(BookingCreate):
    id: int
    status: str

    
class BookingUpdateTime(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None

