import pytest
from app.services.qdrant_client import QdrantService
from app.config import settings

def test_live_qdrant_connectivity():
    """
    Integration test asserting that the Qdrant Cloud cluster is reachable 
    and that collections can be queried.
    """
    service = QdrantService()
    
    # Perform standard ping or collection list
    collections_res = service.client.get_collections()
    assert collections_res is not None
    
    # Print collections for logging purposes
    names = [c.name for c in collections_res.collections]
    print(f"Found Qdrant collections: {names}")
    
    # Assert connection succeeded (no exception raised)
    assert isinstance(names, list)
