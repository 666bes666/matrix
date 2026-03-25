import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.enums import CampaignStatus
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentRead,
    AssessmentScoreSubmit,
    CampaignCreate,
    CampaignRead,
)
from app.services.assessment import AssessmentService

router = APIRouter(prefix="/assessments", tags=["assessments"])

ERROR_MAP = {
    "not_found": (status.HTTP_404_NOT_FOUND, "Не найдено"),
    "duplicate": (status.HTTP_409_CONFLICT, "Оценка уже существует"),
    "invalid_dates": (status.HTTP_400_BAD_REQUEST, "Дата окончания должна быть позже даты начала"),
}


def _raise(code: str) -> None:
    status_code, detail = ERROR_MAP.get(code, (400, code))
    raise HTTPException(status_code=status_code, detail=detail)


@router.get("/campaigns", response_model=list[CampaignRead])
async def list_campaigns(
    campaign_status: CampaignStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AssessmentService(db)
    return await service.list_campaigns(current_user, campaign_status)


@router.post(
    "/campaigns",
    response_model=CampaignRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "head", "department_head")),
):
    service = AssessmentService(db)
    try:
        campaign = await service.create_campaign(data, current_user)
    except ValueError as e:
        _raise(str(e))
    return campaign


@router.get("/campaigns/{campaign_id}", response_model=CampaignRead)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = AssessmentService(db)
    try:
        campaign = await service.get_campaign(campaign_id)
    except ValueError as e:
        _raise(str(e))
    return campaign


@router.post("", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    data: AssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "team_lead", "department_head")),
):
    service = AssessmentService(db)
    try:
        assessment = await service.create_assessment(data, current_user)
    except ValueError as e:
        _raise(str(e))
    return assessment


@router.get("", response_model=list[AssessmentRead])
async def list_assessments(
    campaign_id: uuid.UUID | None = Query(default=None),
    assessee_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AssessmentService(db)
    return await service.list_assessments(current_user, campaign_id, assessee_id)


@router.get("/{assessment_id}", response_model=AssessmentRead)
async def get_assessment(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = AssessmentService(db)
    try:
        assessment = await service.get_assessment(assessment_id)
    except ValueError as e:
        _raise(str(e))
    return assessment


@router.post("/{assessment_id}/scores", response_model=AssessmentRead)
async def submit_scores(
    assessment_id: uuid.UUID,
    data: AssessmentScoreSubmit,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = AssessmentService(db)
    try:
        assessment = await service.submit_scores(assessment_id, data)
    except ValueError as e:
        _raise(str(e))
    return assessment
