import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "backend"))

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.competency import Competency, CompetencyCategory
from app.models.department import Department
from app.models.enums import CompetencyCategoryType, UserRole
from app.models.target_profile import TargetProfile
from app.models.user import User
from tests.backend.conftest import get_auth_headers


@pytest_asyncio.fixture
async def dept(db: AsyncSession) -> Department:
    d = Department(name=f"TP Dept {uuid.uuid4().hex[:8]}", sort_order=50)
    db.add(d)
    await db.flush()
    return d


@pytest_asyncio.fixture
async def category(db: AsyncSession) -> CompetencyCategory:
    cat = CompetencyCategory(
        name=CompetencyCategoryType.SOFT_SKILL,
        description="Soft skills",
    )
    db.add(cat)
    await db.flush()
    return cat


@pytest_asyncio.fixture
async def competency(db: AsyncSession, category: CompetencyCategory) -> Competency:
    comp = Competency(
        category_id=category.id,
        name=f"Competency {uuid.uuid4().hex[:8]}",
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
async def hr_user(db: AsyncSession) -> User:
    user = User(
        email=f"hr_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("HrPass1234"),
        first_name="HR",
        last_name="User",
        role=UserRole.HR,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def target_profile(db: AsyncSession, dept: Department) -> TargetProfile:
    tp = TargetProfile(
        name=f"Profile {uuid.uuid4().hex[:8]}",
        department_id=dept.id,
        position=f"pos_{uuid.uuid4().hex[:6]}",
    )
    db.add(tp)
    await db.flush()
    return tp


async def _admin_headers(client: AsyncClient, admin_user: User) -> dict:
    return await get_auth_headers(client, admin_user.email, "AdminPass1")


async def _user_headers(client: AsyncClient, active_user: User) -> dict:
    return await get_auth_headers(client, active_user.email, "TestPass1")


async def _hr_headers(client: AsyncClient, hr_user: User) -> dict:
    return await get_auth_headers(client, hr_user.email, "HrPass1234")


@pytest.mark.asyncio
async def test_list_target_profiles_empty(
    client: AsyncClient, admin_user: User, dept: Department
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.get(
        f"/api/v1/target-profiles?department_id={dept.id}", headers=headers
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_target_profiles_with_data(
    client: AsyncClient, admin_user: User, target_profile: TargetProfile, dept: Department
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.get("/api/v1/target-profiles", headers=headers)
    assert resp.status_code == 200
    ids = [p["id"] for p in resp.json()]
    assert str(target_profile.id) in ids


@pytest.mark.asyncio
async def test_list_target_profiles_filter_by_dept(
    client: AsyncClient, admin_user: User, target_profile: TargetProfile, dept: Department, db: AsyncSession
):
    other_dept = Department(name=f"Other {uuid.uuid4().hex[:8]}", sort_order=99)
    db.add(other_dept)
    await db.flush()

    headers = await _admin_headers(client, admin_user)
    resp = await client.get(
        f"/api/v1/target-profiles?department_id={dept.id}", headers=headers
    )
    assert resp.status_code == 200
    for p in resp.json():
        assert p["department_id"] == str(dept.id)


@pytest.mark.asyncio
async def test_create_target_profile_as_admin(
    client: AsyncClient, admin_user: User, dept: Department
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.post(
        "/api/v1/target-profiles",
        json={
            "name": f"New Profile {uuid.uuid4().hex[:8]}",
            "department_id": str(dept.id),
            "position": f"engineer_{uuid.uuid4().hex[:6]}",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["department_id"] == str(dept.id)


@pytest.mark.asyncio
async def test_create_target_profile_employee_blocked(
    client: AsyncClient, active_user: User, dept: Department
):
    headers = await _user_headers(client, active_user)
    resp = await client.post(
        "/api/v1/target-profiles",
        json={
            "name": "Profile",
            "department_id": str(dept.id),
        },
        headers=headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_target_profile_duplicate_position_409(
    client: AsyncClient, admin_user: User, dept: Department
):
    headers = await _admin_headers(client, admin_user)
    position = f"pos_{uuid.uuid4().hex[:8]}"
    resp1 = await client.post(
        "/api/v1/target-profiles",
        json={"name": "Profile A", "department_id": str(dept.id), "position": position},
        headers=headers,
    )
    assert resp1.status_code == 201
    resp2 = await client.post(
        "/api/v1/target-profiles",
        json={"name": "Profile B", "department_id": str(dept.id), "position": position},
        headers=headers,
    )
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_get_target_profile_existing(
    client: AsyncClient, admin_user: User, target_profile: TargetProfile
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.get(f"/api/v1/target-profiles/{target_profile.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == str(target_profile.id)


@pytest.mark.asyncio
async def test_get_target_profile_not_found(client: AsyncClient, admin_user: User):
    headers = await _admin_headers(client, admin_user)
    resp = await client.get(f"/api/v1/target-profiles/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_target_profile(
    client: AsyncClient, admin_user: User, target_profile: TargetProfile
):
    headers = await _admin_headers(client, admin_user)
    new_name = f"Updated {uuid.uuid4().hex[:8]}"
    resp = await client.patch(
        f"/api/v1/target-profiles/{target_profile.id}",
        json={"name": new_name},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == new_name


@pytest.mark.asyncio
async def test_delete_target_profile(
    client: AsyncClient, admin_user: User, dept: Department
):
    headers = await _admin_headers(client, admin_user)
    create_resp = await client.post(
        "/api/v1/target-profiles",
        json={"name": f"To Delete {uuid.uuid4().hex[:8]}", "department_id": str(dept.id)},
        headers=headers,
    )
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/target-profiles/{profile_id}", headers=headers)
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_set_competencies_replace_all(
    client: AsyncClient,
    admin_user: User,
    target_profile: TargetProfile,
    competency: Competency,
):
    headers = await _admin_headers(client, admin_user)
    resp = await client.put(
        f"/api/v1/target-profiles/{target_profile.id}/competencies",
        json=[
            {
                "competency_id": str(competency.id),
                "required_level": 2,
                "is_mandatory": True,
            }
        ],
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["competencies"]) == 1
    assert data["competencies"][0]["required_level"] == 2
    assert data["competencies"][0]["is_mandatory"] is True

    resp2 = await client.put(
        f"/api/v1/target-profiles/{target_profile.id}/competencies",
        json=[],
        headers=headers,
    )
    assert resp2.status_code == 200
    assert len(resp2.json()["competencies"]) == 0


@pytest.mark.asyncio
async def test_gap_analysis_returns_list(
    client: AsyncClient,
    admin_user: User,
    target_profile: TargetProfile,
    competency: Competency,
    active_user: User,
):
    headers = await _admin_headers(client, admin_user)
    await client.put(
        f"/api/v1/target-profiles/{target_profile.id}/competencies",
        json=[
            {
                "competency_id": str(competency.id),
                "required_level": 3,
                "is_mandatory": False,
            }
        ],
        headers=headers,
    )
    resp = await client.get(
        f"/api/v1/target-profiles/{target_profile.id}/gap/{active_user.id}",
        headers=headers,
    )
    assert resp.status_code == 200
    gap = resp.json()
    assert isinstance(gap, list)
    assert len(gap) == 1
    entry = gap[0]
    assert entry["competency_id"] == str(competency.id)
    assert entry["required_level"] == 3
    assert entry["current_score"] is None
