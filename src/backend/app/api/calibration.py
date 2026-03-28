import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.services.calibration import CalibrationService

router = APIRouter(prefix="/calibration", tags=["calibration"])


class ResolveRequest(BaseModel):
    adjusted_score: float
    comment: str | None = None


@router.post("/campaigns/{campaign_id}/detect")
async def detect_flags(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "head", "department_head")),
):
    flags = await CalibrationService(db).detect_flags(campaign_id)
    return {"detected": len(flags)}


@router.get("/campaigns/{campaign_id}/flags")
async def list_flags(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "head", "department_head")),
):
    return await CalibrationService(db).list_flags(campaign_id)


@router.post("/flags/{flag_id}/resolve", status_code=status.HTTP_204_NO_CONTENT)
async def resolve_flag(
    flag_id: uuid.UUID,
    data: ResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "head", "department_head")),
):
    try:
        await CalibrationService(db).resolve_flag(
            flag_id, current_user.id, data.adjusted_score, data.comment
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
