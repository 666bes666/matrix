import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "backend"))

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.assessment import (
    AggregatedScore,
    Assessment,
    AssessmentCampaign,
    AssessmentScore,
    CalibrationFlag,
)
from app.models.competency import Competency, CompetencyCategory
from app.models.department import Department
from app.models.enums import (
    AssessmentStatus,
    AssessorType,
    CampaignScope,
    CampaignStatus,
    CompetencyCategoryType,
    NotificationCategory,
    UserRole,
)
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate
from app.services.notification import NotificationService
from tests.backend.conftest import get_auth_headers


@pytest_asyncio.fixture
async def dept(db: AsyncSession) -> Department:
    d = Department(name=f"P5 Dept {uuid.uuid4().hex[:8]}", sort_order=99)
    db.add(d)
    await db.flush()
    return d


@pytest_asyncio.fixture
async def category(db: AsyncSession) -> CompetencyCategory:
    cat = CompetencyCategory(
        name=CompetencyCategoryType.HARD_SKILL,
        description="P5 hard skills",
    )
    db.add(cat)
    await db.flush()
    return cat


@pytest_asyncio.fixture
async def competency(db: AsyncSession, category: CompetencyCategory) -> Competency:
    comp = Competency(
        category_id=category.id,
        name=f"P5 Comp {uuid.uuid4().hex[:8]}",
    )
    db.add(comp)
    await db.flush()
    return comp


@pytest_asyncio.fixture
async def employee(db: AsyncSession, dept: Department) -> User:
    u = User(
        email=f"p5emp_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("TestPass1"),
        first_name="Emp",
        last_name="P5",
        role=UserRole.EMPLOYEE,
        department_id=dept.id,
        is_active=True,
    )
    db.add(u)
    await db.flush()
    return u


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    u = User(
        email=f"p5admin_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("AdminPass1"),
        first_name="Admin",
        last_name="P5",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(u)
    await db.flush()
    return u


@pytest_asyncio.fixture
async def campaign(db: AsyncSession) -> AssessmentCampaign:
    today = date.today()
    c = AssessmentCampaign(
        name=f"P5 Campaign {uuid.uuid4().hex[:8]}",
        scope=CampaignScope.DIVISION,
        start_date=today,
        end_date=today + timedelta(days=30),
        status=CampaignStatus.CALIBRATION,
    )
    db.add(c)
    await db.flush()
    return c


@pytest_asyncio.fixture
async def active_campaign(db: AsyncSession) -> AssessmentCampaign:
    today = date.today()
    c = AssessmentCampaign(
        name=f"P5 Active Campaign {uuid.uuid4().hex[:8]}",
        scope=CampaignScope.DIVISION,
        start_date=today,
        end_date=today + timedelta(days=30),
        status=CampaignStatus.ACTIVE,
    )
    db.add(c)
    await db.flush()
    return c


class TestNotificationService:
    async def test_create_notification(self, db: AsyncSession, employee: User):
        svc = NotificationService(db)
        data = NotificationCreate(
            user_id=employee.id,
            category=NotificationCategory.SYSTEM,
            title="Test title",
            message="Test message",
        )
        n = await svc.create(data)
        assert n.id is not None
        assert n.user_id == employee.id
        assert n.title == "Test title"
        assert n.is_read is False

    async def test_list_notifications(self, db: AsyncSession, employee: User):
        svc = NotificationService(db)
        for i in range(3):
            await svc.create(
                NotificationCreate(
                    user_id=employee.id,
                    category=NotificationCategory.ASSESSMENT,
                    title=f"Notif {i}",
                    message="msg",
                )
            )
        result = await svc.list_for_user(employee.id)
        assert len(result) >= 3

    async def test_mark_read(self, db: AsyncSession, employee: User):
        svc = NotificationService(db)
        n = await svc.create(
            NotificationCreate(
                user_id=employee.id,
                category=NotificationCategory.IDP,
                title="Mark me",
                message="msg",
            )
        )
        assert n.is_read is False
        await svc.mark_read(n.id, employee.id)
        await db.refresh(n)
        assert n.is_read is True

    async def test_mark_all_read(self, db: AsyncSession, employee: User):
        svc = NotificationService(db)
        for i in range(3):
            await svc.create(
                NotificationCreate(
                    user_id=employee.id,
                    category=NotificationCategory.CAREER,
                    title=f"Unread {i}",
                    message="msg",
                )
            )
        await svc.mark_all_read(employee.id)
        count = await svc.unread_count(employee.id)
        assert count == 0

    async def test_unread_count(self, db: AsyncSession, employee: User):
        svc = NotificationService(db)
        initial = await svc.unread_count(employee.id)
        await svc.create(
            NotificationCreate(
                user_id=employee.id,
                category=NotificationCategory.SYSTEM,
                title="Count me",
                message="msg",
            )
        )
        after = await svc.unread_count(employee.id)
        assert after == initial + 1


class TestCalibrationService:
    async def test_detect_flags_with_spread(
        self,
        db: AsyncSession,
        campaign: AssessmentCampaign,
        employee: User,
        admin_user: User,
        competency: Competency,
    ):
        assessor2 = User(
            email=f"p5a2_{uuid.uuid4().hex[:8]}@example.com",
            password_hash=hash_password("TestPass1"),
            first_name="A2",
            last_name="P5",
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        db.add(assessor2)
        await db.flush()

        a1 = Assessment(
            campaign_id=campaign.id,
            assessee_id=employee.id,
            assessor_id=admin_user.id,
            assessor_type=AssessorType.TEAM_LEAD,
            status=AssessmentStatus.COMPLETED,
        )
        a2 = Assessment(
            campaign_id=campaign.id,
            assessee_id=employee.id,
            assessor_id=assessor2.id,
            assessor_type=AssessorType.PEER,
            status=AssessmentStatus.COMPLETED,
        )
        db.add(a1)
        db.add(a2)
        await db.flush()

        s1 = AssessmentScore(
            assessment_id=a1.id,
            competency_id=competency.id,
            score=1,
            is_draft=False,
        )
        s2 = AssessmentScore(
            assessment_id=a2.id,
            competency_id=competency.id,
            score=4,
            is_draft=False,
        )
        db.add(s1)
        db.add(s2)
        await db.flush()

        from app.services.calibration import CalibrationService
        svc = CalibrationService(db)
        flags = await svc.detect_flags(campaign.id)
        assert len(flags) >= 1
        flag = flags[0]
        assert flag.max_spread >= 2
        assert flag.resolved is False

    async def test_detect_flags_no_spread(
        self,
        db: AsyncSession,
        campaign: AssessmentCampaign,
        employee: User,
        admin_user: User,
        competency: Competency,
    ):
        assessor3 = User(
            email=f"p5a3_{uuid.uuid4().hex[:8]}@example.com",
            password_hash=hash_password("TestPass1"),
            first_name="A3",
            last_name="P5",
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        db.add(assessor3)
        await db.flush()

        comp2 = Competency(
            category_id=competency.category_id,
            name=f"P5 NoSpread {uuid.uuid4().hex[:8]}",
        )
        db.add(comp2)
        await db.flush()

        a3 = Assessment(
            campaign_id=campaign.id,
            assessee_id=employee.id,
            assessor_id=assessor3.id,
            assessor_type=AssessorType.SELF,
            status=AssessmentStatus.COMPLETED,
        )
        db.add(a3)
        await db.flush()

        s3 = AssessmentScore(
            assessment_id=a3.id,
            competency_id=comp2.id,
            score=2,
            is_draft=False,
        )
        db.add(s3)
        await db.flush()

        from app.services.calibration import CalibrationService
        svc = CalibrationService(db)
        flags_before = len(await svc.detect_flags(campaign.id))
        flags_after_nospread = [
            f for f in await svc.detect_flags(campaign.id)
            if str(f.competency_id) == str(comp2.id)
        ]
        assert len(flags_after_nospread) == 0

    async def test_list_flags(
        self,
        db: AsyncSession,
        campaign: AssessmentCampaign,
        employee: User,
        competency: Competency,
    ):
        flag = CalibrationFlag(
            campaign_id=campaign.id,
            assessee_id=employee.id,
            competency_id=competency.id,
            max_spread=3,
            resolved=False,
        )
        db.add(flag)
        await db.flush()

        from app.services.calibration import CalibrationService
        svc = CalibrationService(db)
        flags = await svc.list_flags(campaign.id)
        ids = [f["id"] for f in flags]
        assert str(flag.id) in ids

    async def test_resolve_flag(
        self,
        db: AsyncSession,
        campaign: AssessmentCampaign,
        employee: User,
        competency: Competency,
        admin_user: User,
    ):
        agg = AggregatedScore(
            campaign_id=campaign.id,
            user_id=employee.id,
            competency_id=competency.id,
            final_score=2.0,
        )
        db.add(agg)
        flag = CalibrationFlag(
            campaign_id=campaign.id,
            assessee_id=employee.id,
            competency_id=competency.id,
            max_spread=2,
            resolved=False,
        )
        db.add(flag)
        await db.flush()

        from app.services.calibration import CalibrationService
        svc = CalibrationService(db)
        await svc.resolve_flag(flag.id, admin_user.id, 3.0, "calibrated")

        await db.refresh(flag)
        await db.refresh(agg)
        assert flag.resolved is True
        assert float(agg.final_score) == pytest.approx(3.0)


class TestDashboardStats:
    async def test_stats_returns_correct_structure(
        self,
        client: AsyncClient,
        admin_user: User,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get("/api/v1/dashboard/stats", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "pending_assessments" in data
        assert "active_campaigns" in data
        assert "open_idp_goals" in data
        assert "unread_notifications" in data
        assert "user_name" in data
        assert "user_role" in data

    async def test_stats_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/stats")
        assert resp.status_code == 401

    async def test_stats_pending_assessments_count(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        employee: User,
        campaign: AssessmentCampaign,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")

        resp_before = await client.get("/api/v1/dashboard/stats", headers=headers)
        before_count = resp_before.json()["pending_assessments"]

        a = Assessment(
            campaign_id=campaign.id,
            assessee_id=employee.id,
            assessor_id=admin_user.id,
            assessor_type=AssessorType.DEPARTMENT_HEAD,
            status=AssessmentStatus.PENDING,
        )
        db.add(a)
        await db.flush()

        resp_after = await client.get("/api/v1/dashboard/stats", headers=headers)
        after_count = resp_after.json()["pending_assessments"]
        assert after_count == before_count + 1

    async def test_stats_active_campaigns_count(
        self,
        client: AsyncClient,
        admin_user: User,
        active_campaign: AssessmentCampaign,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get("/api/v1/dashboard/stats", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["active_campaigns"] >= 1
