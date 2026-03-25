import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import AssessmentStatus, AssessorType, CampaignScope, CampaignStatus


class ScoreInput(BaseModel):
    competency_id: uuid.UUID
    score: int
    comment: str | None = None


class AssessmentCreate(BaseModel):
    campaign_id: uuid.UUID
    assessee_id: uuid.UUID
    assessor_type: AssessorType


class AssessmentScoreSubmit(BaseModel):
    scores: list[ScoreInput]
    is_draft: bool = True


class AssessmentScoreRead(BaseModel):
    competency_id: uuid.UUID
    score: int
    comment: str | None
    is_draft: bool
    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    model_config = {"from_attributes": True}


class AssessmentRead(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    assessee: UserBrief
    assessor: UserBrief
    assessor_type: AssessorType
    status: AssessmentStatus
    scores: list[AssessmentScoreRead] = []
    created_at: datetime
    model_config = {"from_attributes": True}


class CampaignCreate(BaseModel):
    name: str
    description: str | None = None
    scope: CampaignScope
    department_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    start_date: date
    end_date: date


class CampaignRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    scope: CampaignScope
    status: CampaignStatus
    department_id: uuid.UUID | None
    team_id: uuid.UUID | None
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
