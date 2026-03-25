import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import AggregatedScore
from app.models.target_profile import TargetProfile, TargetProfileCompetency
from app.schemas.target_profile import (
    TargetProfileCompetencyInput,
    TargetProfileCreate,
    TargetProfileUpdate,
)


class TargetProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_dept(self, department_id: uuid.UUID | None) -> list[TargetProfile]:
        stmt = (
            select(TargetProfile)
            .options(
                selectinload(TargetProfile.department),
                selectinload(TargetProfile.competencies).selectinload(
                    TargetProfileCompetency.competency
                ),
            )
            .order_by(TargetProfile.name)
        )
        if department_id is not None:
            stmt = stmt.where(TargetProfile.department_id == department_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, profile_id: uuid.UUID) -> TargetProfile:
        result = await self.db.execute(
            select(TargetProfile)
            .options(
                selectinload(TargetProfile.department),
                selectinload(TargetProfile.competencies).selectinload(
                    TargetProfileCompetency.competency
                ),
            )
            .where(TargetProfile.id == profile_id)
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            raise ValueError("not_found")
        return profile

    async def create(self, data: TargetProfileCreate) -> TargetProfile:
        if data.position is not None:
            existing = await self.db.execute(
                select(TargetProfile).where(
                    TargetProfile.department_id == data.department_id,
                    TargetProfile.position == data.position,
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("name_taken")
        profile = TargetProfile(
            name=data.name,
            department_id=data.department_id,
            position=data.position,
            description=data.description,
        )
        self.db.add(profile)
        await self.db.flush()
        return await self.get_by_id(profile.id)

    async def update(self, profile_id: uuid.UUID, data: TargetProfileUpdate) -> TargetProfile:
        profile = await self.get_by_id(profile_id)
        if data.name is not None:
            profile.name = data.name
        if data.position is not None:
            profile.position = data.position
        if data.description is not None:
            profile.description = data.description
        await self.db.flush()
        return await self.get_by_id(profile_id)

    async def delete(self, profile_id: uuid.UUID) -> None:
        profile = await self.get_by_id(profile_id)
        await self.db.delete(profile)
        await self.db.flush()

    async def set_competencies(
        self, profile_id: uuid.UUID, competencies: list[TargetProfileCompetencyInput]
    ) -> TargetProfile:
        await self.db.execute(
            delete(TargetProfileCompetency).where(
                TargetProfileCompetency.target_profile_id == profile_id
            )
        )
        for item in competencies:
            tpc = TargetProfileCompetency(
                target_profile_id=profile_id,
                competency_id=item.competency_id,
                required_level=item.required_level,
                is_mandatory=item.is_mandatory,
            )
            self.db.add(tpc)
        await self.db.flush()
        result = await self.db.execute(
            select(TargetProfile)
            .options(
                selectinload(TargetProfile.department),
                selectinload(TargetProfile.competencies).selectinload(
                    TargetProfileCompetency.competency
                ),
            )
            .where(TargetProfile.id == profile_id)
            .execution_options(populate_existing=True)
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            raise ValueError("not_found")
        return profile

    async def get_gap(self, profile_id: uuid.UUID, user_id: uuid.UUID) -> list[dict]:
        profile = await self.get_by_id(profile_id)
        result = []
        for tpc in profile.competencies:
            agg_result = await self.db.execute(
                select(AggregatedScore)
                .where(
                    AggregatedScore.user_id == user_id,
                    AggregatedScore.competency_id == tpc.competency_id,
                )
                .order_by(AggregatedScore.campaign_id.desc())
                .limit(1)
            )
            agg = agg_result.scalar_one_or_none()
            current_score = float(agg.final_score) if agg is not None else None
            result.append(
                {
                    "competency_id": tpc.competency_id,
                    "competency_name": tpc.competency.name,
                    "required_level": tpc.required_level,
                    "is_mandatory": tpc.is_mandatory,
                    "current_score": current_score,
                }
            )
        return result
