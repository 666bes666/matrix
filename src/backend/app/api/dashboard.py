from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.assessment import Assessment, AssessmentCampaign
from app.models.development_plan import DevelopmentGoal, DevelopmentPlan
from app.models.enums import AssessmentStatus, CampaignStatus, GoalStatus
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pending_assessments_result = await db.execute(
        select(Assessment).where(
            Assessment.assessor_id == current_user.id,
            Assessment.status == AssessmentStatus.PENDING,
        )
    )
    pending_assessments = len(pending_assessments_result.scalars().all())

    active_campaigns_result = await db.execute(
        select(AssessmentCampaign).where(
            AssessmentCampaign.status == CampaignStatus.ACTIVE
        )
    )
    active_campaigns = len(active_campaigns_result.scalars().all())

    my_plans_result = await db.execute(
        select(DevelopmentPlan).where(
            DevelopmentPlan.user_id == current_user.id,
            DevelopmentPlan.is_archived.is_(False),
        )
    )
    my_plans = my_plans_result.scalars().all()
    plan_ids = [p.id for p in my_plans]

    open_goals = 0
    if plan_ids:
        goals_result = await db.execute(
            select(DevelopmentGoal).where(
                DevelopmentGoal.plan_id.in_(plan_ids),
                DevelopmentGoal.status.in_([GoalStatus.PLANNED, GoalStatus.IN_PROGRESS]),
            )
        )
        open_goals = len(goals_result.scalars().all())

    unread_result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
    )
    unread_notifications = len(unread_result.scalars().all())

    return {
        "pending_assessments": pending_assessments,
        "active_campaigns": active_campaigns,
        "open_idp_goals": open_goals,
        "unread_notifications": unread_notifications,
        "user_name": f"{current_user.last_name} {current_user.first_name}",
        "user_role": current_user.role.value,
    }
