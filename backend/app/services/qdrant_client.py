import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from app.config import settings

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=60.0  # Set high timeout to prevent write timeout issues
        )
        self.collection_name = "spotify_tracks"
        self.vector_size = 384  # bge-small-en-v1.5 output dimension

    def create_collection_if_not_exists(self):
        try:
            collections = self.client.get_collections()
            exist = any(c.name == self.collection_name for c in collections.collections)
            
            if not exist:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully.")
            else:
                logger.info(f"Collection {self.collection_name} already exists.")
        except Exception as e:
            logger.error(f"Failed to create Qdrant collection: {e}")
            raise

    def upsert_tracks(self, points: list[PointStruct]):
        """
        Upsert a batch of points to the Qdrant collection.
        Each point contains ID, Vector embedding, and Metadata payload.
        """
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=points,
                timeout=120
            )
        except Exception as e:
            logger.error(f"Failed to upsert points to Qdrant: {e}")
            raise

    def search_similar_tracks(self, query_vector: list[float], limit: int = 100) -> list:
        """
        Search for tracks similar to the query vector.
        """
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit
            )
            return results.points
        except Exception as e:
            logger.error(f"Failed to search Qdrant: {e}")
            raise
