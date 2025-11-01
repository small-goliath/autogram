"""Basic API tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_announcements(client: AsyncClient):
    """Test get announcements endpoint."""
    response = await client.get("/api/announcements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_admin_login_unauthorized(client: AsyncClient):
    """Test admin login with invalid credentials."""
    response = await client.post(
        "/api/admin/login",
        json={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_endpoint_without_token(client: AsyncClient):
    """Test admin endpoint without authentication."""
    response = await client.get("/api/admin/sns-users")
    assert response.status_code == 403  # Forbidden without token
