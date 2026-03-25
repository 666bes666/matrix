import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import Assessment, AssessmentCampaign, AssessmentScore
from app.models.enums import AssessmentStatus, CampaignStatus
from app.models.user import User
from app.schemas.assessment import AssessmentCreate, AssessmentScoreSubmit, CampaignCreate


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_campaigns(
        self, current_user: User, status: CampaignStatus | None
    ) -> list[AssessmentCampaign]:
        stmt = select(AssessmentCampaign).order_by(AssessmentCampaign.created_at.desc())
        if status is not None:
            stmt = stmt.where(AssessmentCampaign.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_campaign(self, campaign_id: uuid.UUID) -> AssessmentCampaign:
        result = await self.db.execute(
            select(AssessmentCampaign).where(AssessmentCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if campaign is None:
            raise ValueError("not_found")
        return campaign

    async def create_campaign(
        self, data: CampaignCreate, current_user: User
    ) -> AssessmentCampaign:
        if data.end_date <= data.start_date:
            raise ValueError("invalid_dates")
        campaign = AssessmentCampaign(
            name=data.name,
            description=data.description,
            scope=data.scope,
            department_id=data.department_id,
            team_id=data.team_id,
            start_date=data.start_date,
            end_date=data.end_date,
            created_by=current_user.id,
        )
        self.db.add(campaign)
        await self.db.flush()
        return await self.get_campaign(campaign.id)

    async def create_assessment(
        self, data: AssessmentCreate, current_user: User
    ) -> Assessment:
        campaign = await self.get_campaign(data.campaign_id)
        if campaign is None:
            raise ValueError("not_found")
        existing = await self.db.execute(
            select(Assessment).where(
                Assessment.campaign_id == data.campaign_id,
                Assessment.assessee_id == data.assessee_id,
                Assessment.assessor_id == current_user.id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("duplicate")
        assessment = Assessment(
            campaign_id=data.campaign_id,
            assessee_id=data.assessee_id,
            assessor_id=current_user.id,
            assessor_type=data.assessor_type,
        )
        self.db.add(assessment)
        await self.db.flush()
        return await self.get_assessment(assessment.id)

    async def submit_scores(
        self, assessment_id: uuid.UUID, data: AssessmentScoreSubmit
    ) -> Assessment:
        assessment = await self.get_assessment(assessment_id)
        for score_input in data.scores:
            existing = await self.db.execute(
                select(AssessmentScore).where(
                    AssessmentScore.assessment_id == assessment_id,
                    AssessmentScore.competency_id == score_input.competency_id,
                )
            )
            score_obj = existing.scalar_one_or_none()
            if score_obj is None:
                score_obj = AssessmentScore(
                    assessment_id=assessment_id,
                    competency_id=score_input.competency_id,
                    score=score_input.score,
                    comment=score_input.comment,
                    is_draft=data.is_draft,
                )
                self.db.add(score_obj)
            else:
                score_obj.score = score_input.score
                score_obj.comment = score_input.comment
                score_obj.is_draft = data.is_draft
        if not data.is_draft:
            assessment.status = AssessmentStatus.COMPLETED
            assessment.completed_at = datetime.now(UTC)
        await self.db.flush()
        result = await self.db.execute(
            select(Assessment)
            .options(
                selectinload(Assessment.assessee),
                selectinload(Assessment.assessor),
                selectinload(Assessment.scores),
            )
            .where(Assessment.id == assessment_id)
            .execution_options(populate_existing=True)
        )
        assessment = result.scalar_one_or_none()
        if assessment is None:
            raise ValueError("not_found")
        return assessment

    async def get_assessment(self, assessment_id: uuid.UUID) -> Assessment:
        result = await self.db.execute(
            select(Assessment)
            .options(
                selectinload(Assessment.assessee),
                selectinload(Assessment.assessor),
                selectinload(Assessment.scores),
            )
            .where(Assessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        if assessment is None:
            raise ValueError("not_found")
        return assessment

    async def list_assessments(
        self,
        current_user: User,
        campaign_id: uuid.UUID | None,
        assessee_id: uuid.UUID | None,
    ) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .options(
                selectinload(Assessment.assessee),
                selectinload(Assessment.assessor),
                selectinload(Assessment.scores),
            )
            .order_by(Assessment.created_at.desc())
        )
        if campaign_id is not None:
            stmt = stmt.where(Assessment.campaign_id == campaign_id)
        if assessee_id is not None:
            stmt = stmt.where(Assessment.assessee_id == assessee_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
