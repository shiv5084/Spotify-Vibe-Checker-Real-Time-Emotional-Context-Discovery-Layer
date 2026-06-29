from unittest.mock import patch, MagicMock

def test_health_check_success(client):
    """
    Test GET /api/health returns a successful health response.
    """
    # Mock services inside the router module
    with patch("app.routers.health.CacheService") as mock_cache_class, \
         patch("app.routers.health.QdrantService") as mock_qdrant_class, \
         patch("app.routers.health.create_client") as mock_create_client:
         
        # Setup mock cache instance
        mock_cache = MagicMock()
        mock_cache.redis_enabled = True
        mock_cache_class.return_value = mock_cache

        # Setup mock qdrant instance
        mock_qdrant = MagicMock()
        mock_qdrant_class.return_value = mock_qdrant

        # Setup mock supabase instance
        mock_supabase = MagicMock()
        mock_supabase_query = MagicMock()
        mock_supabase_query.select.return_value.limit.return_value.execute.return_value = MagicMock()
        mock_supabase.table.return_value = mock_supabase_query
        mock_create_client.return_value = mock_supabase

        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["redis"] == "healthy"
        assert data["services"]["qdrant"] == "healthy"
        assert data["services"]["supabase"] == "healthy"
