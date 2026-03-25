import uuid
from datetime import datetime

from pydantic import BaseModel


class TargetProfileCompetencyInput(BaseModel):
    competency_id: uuid.UUID
    required_level: int
    is_mandatory: bool = False


class TargetProfileCreate(BaseModel):
    name: str
    department_id: uuid.UUID
    position: str | None = None
    description: str | None = None


class TargetProfileUpdate(BaseModel):
    name: str | None = None
    position: str | None = None
    description: str | None = None


class CompetencyBrief(BaseModel):
    id: uuid.UUID
    name: str
    model_config = {"from_attributes": True}


class TargetProfileCompetencyRead(BaseModel):
    competency_id: uuid.UUID
    required_level: int
    is_mandatory: bool
    competency: CompetencyBrief
    model_config = {"from_attributes": True}


class DepartmentBrief(BaseModel):
    id: uuid.UUID
    name: str
    model_config = {"from_attributes": True}


class TargetProfileRead(BaseModel):
    id: uuid.UUID
    name: str
    department_id: uuid.UUID
    department: DepartmentBrief
    position: str | None
    description: str | None
    competencies: list[TargetProfileCompetencyRead] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
