import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.assessment import AggregatedScore
from app.models.competency import Competency
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/matrix")
async def get_matrix(
    department_id: uuid.UUID | None = Query(None),
    team_id: uuid.UUID | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users_query = (
        select(User)
        .options(selectinload(User.department), selectinload(User.team))
        .where(User.is_active.is_(True))
    )

    if current_user.role == UserRole.TEAM_LEAD:
        users_query = users_query.where(User.team_id == current_user.team_id)
    elif current_user.role == UserRole.DEPARTMENT_HEAD:
        users_query = users_query.where(User.department_id == current_user.department_id)
    elif current_user.role == UserRole.EMPLOYEE:
        users_query = users_query.where(User.id == current_user.id)

    if department_id is not None:
        users_query = users_query.where(User.department_id == department_id)
    if team_id is not None:
        users_query = users_query.where(User.team_id == team_id)

    users_result = await db.execute(users_query)
    users = list(users_result.scalars().all())

    comp_query = select(Competency).where(Competency.is_archived.is_(False))
    if category_id is not None:
        comp_query = comp_query.where(Competency.category_id == category_id)
    comp_query = comp_query.order_by(Competency.name)
    comp_result = await db.execute(comp_query)
    competencies = list(comp_result.scalars().all())

    user_ids = [u.id for u in users]
    comp_ids = [c.id for c in competencies]

    scores: dict[uuid.UUID, dict[uuid.UUID, float]] = {}
    if user_ids and comp_ids:
        agg_result = await db.execute(
            select(AggregatedScore).where(
                AggregatedScore.user_id.in_(user_ids),
                AggregatedScore.competency_id.in_(comp_ids),
            )
        )
        for agg in agg_result.scalars().all():
            if agg.user_id not in scores:
                scores[agg.user_id] = {}
            scores[agg.user_id][agg.competency_id] = float(agg.final_score)

    return {
        "users": [
            {
                "id": str(u.id),
                "full_name": f"{u.last_name} {u.first_name}",
                "department": u.department.name if u.department else None,
                "team": u.team.name if u.team else None,
            }
            for u in users
        ],
        "competencies": [
            {
                "id": str(c.id),
                "name": c.name,
                "category_id": str(c.category_id),
            }
            for c in competencies
        ],
        "scores": {
            str(uid): {str(cid): score for cid, score in cscores.items()}
            for uid, cscores in scores.items()
        },
    }
