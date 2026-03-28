import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import (
    AggregatedScore,
    Assessment,
    AssessmentScore,
    CalibrationAdjustment,
    CalibrationFlag,
)
from app.models.competency import Competency
from app.models.enums import AssessmentStatus, CalibrationAction
from app.models.user import User


class CalibrationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_flags(self, campaign_id: uuid.UUID) -> list[CalibrationFlag]:
        scores_result = await self.db.execute(
            select(AssessmentScore, Assessment)
            .join(Assessment, AssessmentScore.assessment_id == Assessment.id)
            .where(
                Assessment.campaign_id == campaign_id,
                Assessment.status == AssessmentStatus.COMPLETED,
                AssessmentScore.is_draft.is_(False),
            )
        )
        rows = scores_result.all()

        data: dict[tuple, list[int]] = {}
        for score_row, assessment in rows:
            key = (assessment.assessee_id, score_row.competency_id)
            data.setdefault(key, []).append(score_row.score)

        flags = []
        for (assessee_id, competency_id), scores in data.items():
            if len(scores) < 2:
                continue
            spread = max(scores) - min(scores)
            if spread < 2:
                continue

            existing = await self.db.execute(
                select(CalibrationFlag).where(
                    CalibrationFlag.campaign_id == campaign_id,
                    CalibrationFlag.assessee_id == assessee_id,
                    CalibrationFlag.competency_id == competency_id,
                )
            )
            flag = existing.scalar_one_or_none()
            if flag is None:
                flag = CalibrationFlag(
                    campaign_id=campaign_id,
                    assessee_id=assessee_id,
                    competency_id=competency_id,
                    max_spread=int(spread),
                )
                self.db.add(flag)
            flags.append(flag)

        await self.db.flush()
        return flags

    async def list_flags(self, campaign_id: uuid.UUID) -> list[dict]:
        result = await self.db.execute(
            select(CalibrationFlag, User, Competency)
            .join(User, CalibrationFlag.assessee_id == User.id)
            .join(Competency, CalibrationFlag.competency_id == Competency.id)
            .where(
                CalibrationFlag.campaign_id == campaign_id,
                CalibrationFlag.resolved.is_(False),
            )
        )
        return [
            {
                "id": str(flag.id),
                "assessee_id": str(flag.assessee_id),
                "assessee_name": f"{user.last_name} {user.first_name}",
                "competency_id": str(flag.competency_id),
                "competency_name": competency.name,
                "max_spread": flag.max_spread,
                "resolved": flag.resolved,
            }
            for flag, user, competency in result.all()
        ]

    async def resolve_flag(
        self,
        flag_id: uuid.UUID,
        adjuster_id: uuid.UUID,
        adjusted_score: float,
        comment: str | None,
    ) -> None:
        flag_result = await self.db.execute(
            select(CalibrationFlag).where(CalibrationFlag.id == flag_id)
        )
        flag = flag_result.scalar_one_or_none()
        if flag is None:
            raise ValueError("flag_not_found")

        agg_result = await self.db.execute(
            select(AggregatedScore).where(
                AggregatedScore.campaign_id == flag.campaign_id,
                AggregatedScore.user_id == flag.assessee_id,
                AggregatedScore.competency_id == flag.competency_id,
            )
        )
        agg = agg_result.scalar_one_or_none()
        original_score = float(agg.final_score) if agg else None

        adjustment = CalibrationAdjustment(
            flag_id=flag_id,
            adjusted_by=adjuster_id,
            action=CalibrationAction.ADJUST,
            original_score=original_score,
            adjusted_score=adjusted_score,
            comment=comment,
        )
        self.db.add(adjustment)

        if agg is not None:
            agg.final_score = adjusted_score

        flag.resolved = True
        await self.db.flush()
