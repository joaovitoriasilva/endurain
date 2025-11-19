from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class PersonalRecordBase(BaseModel):
    user_id: int
    activity_id: int
    activity_type: int
    pr_date: datetime
    metric: str
    value: Decimal
    unit: str


class PersonalRecordCreate(PersonalRecordBase):
    pass


class PersonalRecord(PersonalRecordBase):
    id: int

    class Config:
        from_attributes = True
