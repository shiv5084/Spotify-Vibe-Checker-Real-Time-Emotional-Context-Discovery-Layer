from unittest.mock import MagicMock, patch

def test_get_me_unauthorized(client):
    """
    Test GET /api/auth/me returns 401 when no token is provided.
    """
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"

def test_get_me_authorized(client, mock_auth_service):
    """
    Test GET /api/auth/me returns 200 when a valid token is provided.
    """
    # Setup mock verify_token to return valid user details
    mock_auth_service.return_value = {
        "id": "user-uuid-12345",
        "email": "test@example.com",
        "display_name": "Test User",
        "avatar_url": "http://avatar.com/123"
    }

    # Query with mock authorization header
    headers = {"Authorization": "Bearer valid-mock-jwt"}
    response = client.get("/api/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "user-uuid-12345"
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"

def test_authenticate_google_success(client, mock_auth_service):
    """
    Test POST /api/auth/google verifies token and returns login details.
    """
    # Setup mock verify_token
    mock_auth_service.return_value = {
        "id": "user-uuid-12345",
        "email": "test@example.com",
        "display_name": "Test User",
        "avatar_url": "http://avatar.com/123"
    }

    # Mock database table sync call to avoid real db writes
    with patch("supabase.client.Client.table") as mock_supabase:
        mock_query = MagicMock()
        mock_query.upsert.return_value.execute.return_value = MagicMock()
        mock_supabase.return_value = mock_query

        # Send ID Token
        payload = {"id_token": "google-oauth-id-token"}
        response = client.post("/api/auth/google", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "google-oauth-id-token"
        assert data["user"]["email"] == "test@example.com"
