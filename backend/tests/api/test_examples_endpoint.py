def test_get_examples_success(client):
    """
    Test GET /api/examples returns standard prompts correctly.
    """
    response = client.get("/api/examples")
    assert response.status_code == 200
    data = response.json()
    assert "examples" in data
    assert len(data["examples"]) == 6
    assert "Melancholy but hopeful" in data["examples"]
