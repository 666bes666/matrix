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
from app.models.assessment import AssessmentCampaign
from app.models.competency import Competency, CompetencyCategory
from app.models.department import Department
from app.models.enums import CampaignScope, CompetencyCategoryType, UserRole
from app.models.user import User
from tests.backend.conftest import get_auth_headers


@pytest_asyncio.fixture
async def dept(db: AsyncSession) -> Department:
    d = Department(name=f"Assess Dept {uuid.uuid4().hex[:8]}", sort_order=60)
    db.add(d)
    await db.flush()
    return d


@pytest_asyncio.fixture
async def category(db: AsyncSession) -> CompetencyCategory:
    cat = CompetencyCategory(
        name=CompetencyCategoryType.PROCESS,
        description="Process skills",
    )
    db.add(cat)
    await db.flush()
    return cat


@pytest_asyncio.fixture
async def competency(db: AsyncSession, category: CompetencyCategory) -> Competency:
    comp = Competency(
        category_id=category.id,
        name=f"Assess Competency {uuid.uuid4().hex[:8]}",
    )
    db.add(comp)
    await db.flush()
    return comp


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("AdminPass1"),
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def active_user(db: AsyncSession, dept: Department) -> User:
    user = User(
        email=f"user_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("TestPass1"),
        first_name="Test",
        last_name="User",
        role=UserRole.EMPLOYEE,
        department_id=dept.id,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def campaign(db: AsyncSession, admin_user: User) -> AssessmentCampaign:
    today = date.today()
    c = AssessmentCampaign(
        name=f"Campaign {uuid.uuid4().hex[:8]}",
        scope=CampaignScope.DIVISION,
        start_date=today,
        end_date=today + timedelta(days=30),
        created_by=admin_user.id,
    )
    db.add(c)
    await db.flush()
    return c


async def _admin_headers(client: AsyncClient, admin_user: User) -> dict:
    return await get_auth_headers(client, admin_user.email, "AdminPass1")


async def _user_headers(client: AsyncClient, active_user: User) -> dict:
    return await get_auth_headers(client, active_user.email, "TestPass1")


@pytest.mark.asyncio
async def test_create_campaign_as_admin(client: AsyncClient, admin_user: User):
    headers = await _admin_headers(client, admin_user)
    today = date.today()
    resp = await client.post(
        "/api/v1/assessments/campaigns",
        json={
            "name": f"Test Campaign {uuid.uuid4().hex[:8]}",
            "scope": "division",
            "start_date": str(today),
            "end_date": str(today + timedelta(days=14)),
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["scope"] == "division"


@pytest.mark.asyncio
async def test_create_campaign_employee_blocked(client: AsyncClient, active_user: User):
    headers = await _user_headers(client, active_user)
    today = date.today()
    resp = await client.post(
        "/api/v1/assessments/campaigns",
        json={
            "name": "Campaign",
            "scope": "division",
            "start_date": str(today),
            "end_date": str(today + timedelta(days=7)),
        },
        headers=headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_campaign_invalid_dates(client: AsyncClient, admin_user: User):
    headers = await _admin_headers(client, admin_user)
    today = date.today()
    resp = await client.post(
        "/api/v1/assessments/campaigns",
        json={
            "name": "Bad Dates Campaign",
            "scope": "division",
            "start_date": str(today + timedelta(days=5)),
            "end_date": str(today),
        },
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_campaigns(
    client: AsyncClient, admin_user: User, campaign: AssessmentCampaign
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.get("/api/v1/assessments/campaigns", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    ids = [c["id"] for c in resp.json()]
    assert str(campaign.id) in ids


@pytest.mark.asyncio
async def test_get_campaign(
    client: AsyncClient, admin_user: User, campaign: AssessmentCampaign
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.get(f"/api/v1/assessments/campaigns/{campaign.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == str(campaign.id)


@pytest.mark.asyncio
async def test_get_campaign_not_found(client: AsyncClient, admin_user: User):
    headers = await _admin_headers(client, admin_user)
    resp = await client.get(
        f"/api/v1/assessments/campaigns/{uuid.uuid4()}", headers=headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_assessment(
    client: AsyncClient, admin_user: User, active_user: User, campaign: AssessmentCampaign
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.post(
        "/api/v1/assessments",
        json={
            "campaign_id": str(campaign.id),
            "assessee_id": str(active_user.id),
            "assessor_type": "department_head",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["assessee"]["id"] == str(active_user.id)


@pytest.mark.asyncio
async def test_duplicate_assessment_409(
    client: AsyncClient, admin_user: User, active_user: User, campaign: AssessmentCampaign
):
    headers = await _admin_headers(client, admin_user)
    payload = {
        "campaign_id": str(campaign.id),
        "assessee_id": str(active_user.id),
        "assessor_type": "department_head",
    }
    resp1 = await client.post("/api/v1/assessments", json=payload, headers=headers)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/assessments", json=payload, headers=headers)
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_submit_scores_draft(
    client: AsyncClient,
    admin_user: User,
    active_user: User,
    campaign: AssessmentCampaign,
    competency: Competency,
):
    headers = await _admin_headers(client, admin_user)
    create_resp = await client.post(
        "/api/v1/assessments",
        json={
            "campaign_id": str(campaign.id),
            "assessee_id": str(active_user.id),
            "assessor_type": "self",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    assessment_id = create_resp.json()["id"]

    score_resp = await client.post(
        f"/api/v1/assessments/{assessment_id}/scores",
        json={
            "scores": [
                {"competency_id": str(competency.id), "score": 2, "comment": "Good"}
            ],
            "is_draft": True,
        },
        headers=headers,
    )
    assert score_resp.status_code == 200
    data = score_resp.json()
    assert data["status"] == "pending"
    assert len(data["scores"]) == 1
    assert data["scores"][0]["is_draft"] is True


@pytest.mark.asyncio
async def test_submit_scores_final(
    client: AsyncClient,
    admin_user: User,
    active_user: User,
    campaign: AssessmentCampaign,
    competency: Competency,
):
    headers = await _admin_headers(client, admin_user)
    create_resp = await client.post(
        "/api/v1/assessments",
        json={
            "campaign_id": str(campaign.id),
            "assessee_id": str(active_user.id),
            "assessor_type": "peer",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    assessment_id = create_resp.json()["id"]

    score_resp = await client.post(
        f"/api/v1/assessments/{assessment_id}/scores",
        json={
            "scores": [{"competency_id": str(competency.id), "score": 3}],
            "is_draft": False,
        },
        headers=headers,
    )
    assert score_resp.status_code == 200
    data = score_resp.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_get_assessment_with_scores(
    client: AsyncClient,
    admin_user: User,
    active_user: User,
    campaign: AssessmentCampaign,
    competency: Competency,
):
    headers = await _admin_headers(client, admin_user)
    create_resp = await client.post(
        "/api/v1/assessments",
        json={
            "campaign_id": str(campaign.id),
            "assessee_id": str(active_user.id),
            "assessor_type": "team_lead",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    assessment_id = create_resp.json()["id"]

    await client.post(
        f"/api/v1/assessments/{assessment_id}/scores",
        json={
            "scores": [{"competency_id": str(competency.id), "score": 1}],
            "is_draft": True,
        },
        headers=headers,
    )

    get_resp = await client.get(f"/api/v1/assessments/{assessment_id}", headers=headers)
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == assessment_id
    assert len(data["scores"]) == 1


@pytest.mark.asyncio
async def test_list_assessments(
    client: AsyncClient,
    admin_user: User,
    active_user: User,
    campaign: AssessmentCampaign,
):
    headers = await _admin_headers(client, admin_user)
    await client.post(
        "/api/v1/assessments",
        json={
            "campaign_id": str(campaign.id),
            "assessee_id": str(active_user.id),
            "assessor_type": "department_head",
        },
        headers=headers,
    )
    resp = await client.get(
        f"/api/v1/assessments?campaign_id={campaign.id}", headers=headers
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1
