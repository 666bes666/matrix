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
from app.models.assessment import AggregatedScore, AssessmentCampaign
from app.models.competency import Competency, CompetencyCategory
from app.models.department import Department
from app.models.enums import CampaignScope, CampaignStatus, CompetencyCategoryType, UserRole
from app.models.team import Team
from app.models.user import User
from tests.backend.conftest import get_auth_headers


@pytest_asyncio.fixture
async def dept(db: AsyncSession) -> Department:
    d = Department(name=f"Analytics Dept {uuid.uuid4().hex[:8]}", sort_order=70)
    db.add(d)
    await db.flush()
    return d


@pytest_asyncio.fixture
async def team(db: AsyncSession, dept: Department) -> Team:
    t = Team(name=f"Analytics Team {uuid.uuid4().hex[:8]}", department_id=dept.id)
    db.add(t)
    await db.flush()
    return t


@pytest_asyncio.fixture
async def category(db: AsyncSession) -> CompetencyCategory:
    cat = CompetencyCategory(
        name=CompetencyCategoryType.HARD_SKILL,
        description="Hard skills",
    )
    db.add(cat)
    await db.flush()
    return cat


@pytest_asyncio.fixture
async def competency(db: AsyncSession, category: CompetencyCategory) -> Competency:
    comp = Competency(
        category_id=category.id,
        name=f"Analytics Comp {uuid.uuid4().hex[:8]}",
    )
    db.add(comp)
    await db.flush()
    return comp


@pytest_asyncio.fixture
async def employee(db: AsyncSession, dept: Department, team: Team) -> User:
    u = User(
        email=f"emp_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("TestPass1"),
        first_name="Emp",
        last_name="User",
        role=UserRole.EMPLOYEE,
        department_id=dept.id,
        team_id=team.id,
        is_active=True,
    )
    db.add(u)
    await db.flush()
    return u


@pytest_asyncio.fixture
async def team_lead(db: AsyncSession, dept: Department, team: Team) -> User:
    u = User(
        email=f"tl_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("TestPass1"),
        first_name="TL",
        last_name="Lead",
        role=UserRole.TEAM_LEAD,
        department_id=dept.id,
        team_id=team.id,
        is_active=True,
    )
    db.add(u)
    await db.flush()
    return u


@pytest_asyncio.fixture
async def campaign(db: AsyncSession) -> AssessmentCampaign:
    today = date.today()
    c = AssessmentCampaign(
        name=f"Analytics Campaign {uuid.uuid4().hex[:8]}",
        scope=CampaignScope.DIVISION,
        start_date=today,
        end_date=today + timedelta(days=30),
        status=CampaignStatus.ACTIVE,
    )
    db.add(c)
    await db.flush()
    return c


@pytest_asyncio.fixture
async def agg_score(
    db: AsyncSession,
    campaign: AssessmentCampaign,
    employee: User,
    competency: Competency,
) -> AggregatedScore:
    score = AggregatedScore(
        campaign_id=campaign.id,
        user_id=employee.id,
        competency_id=competency.id,
        final_score=3.0,
    )
    db.add(score)
    await db.flush()
    return score


class TestMatrixEndpoint:
    async def test_admin_gets_all_users(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        employee: User,
        competency: Competency,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get("/api/v1/analytics/matrix", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "users" in data
        assert "competencies" in data
        assert "scores" in data

    async def test_matrix_structure(
        self,
        client: AsyncClient,
        admin_user: User,
        employee: User,
        competency: Competency,
        agg_score: AggregatedScore,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get("/api/v1/analytics/matrix", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        user_ids = [u["id"] for u in data["users"]]
        assert str(employee.id) in user_ids
        comp_ids = [c["id"] for c in data["competencies"]]
        assert str(competency.id) in comp_ids

    async def test_scores_populated(
        self,
        client: AsyncClient,
        admin_user: User,
        employee: User,
        competency: Competency,
        agg_score: AggregatedScore,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get("/api/v1/analytics/matrix", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        scores = data["scores"]
        uid = str(employee.id)
        cid = str(competency.id)
        assert uid in scores
        assert cid in scores[uid]
        assert scores[uid][cid] == pytest.approx(3.0)

    async def test_filter_by_department(
        self,
        client: AsyncClient,
        admin_user: User,
        employee: User,
        dept: Department,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get(
            "/api/v1/analytics/matrix",
            headers=headers,
            params={"department_id": str(dept.id)},
        )
        assert resp.status_code == 200
        data = resp.json()
        user_ids = [u["id"] for u in data["users"]]
        assert str(employee.id) in user_ids

    async def test_filter_by_team(
        self,
        client: AsyncClient,
        admin_user: User,
        employee: User,
        team: Team,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get(
            "/api/v1/analytics/matrix",
            headers=headers,
            params={"team_id": str(team.id)},
        )
        assert resp.status_code == 200
        data = resp.json()
        user_ids = [u["id"] for u in data["users"]]
        assert str(employee.id) in user_ids

    async def test_filter_by_category(
        self,
        client: AsyncClient,
        admin_user: User,
        category: CompetencyCategory,
        competency: Competency,
    ):
        headers = await get_auth_headers(client, admin_user.email, "AdminPass1")
        resp = await client.get(
            "/api/v1/analytics/matrix",
            headers=headers,
            params={"category_id": str(category.id)},
        )
        assert resp.status_code == 200
        data = resp.json()
        comp_ids = [c["id"] for c in data["competencies"]]
        assert str(competency.id) in comp_ids

    async def test_team_lead_sees_own_team_only(
        self,
        client: AsyncClient,
        team_lead: User,
        employee: User,
    ):
        headers = await get_auth_headers(client, team_lead.email, "TestPass1")
        resp = await client.get("/api/v1/analytics/matrix", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        user_ids = [u["id"] for u in data["users"]]
        assert str(employee.id) in user_ids
        assert str(team_lead.id) in user_ids

    async def test_employee_sees_only_self(
        self,
        client: AsyncClient,
        employee: User,
        team_lead: User,
    ):
        headers = await get_auth_headers(client, employee.email, "TestPass1")
        resp = await client.get("/api/v1/analytics/matrix", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        user_ids = [u["id"] for u in data["users"]]
        assert str(employee.id) in user_ids
        assert str(team_lead.id) not in user_ids

    async def test_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/analytics/matrix")
        assert resp.status_code == 401
