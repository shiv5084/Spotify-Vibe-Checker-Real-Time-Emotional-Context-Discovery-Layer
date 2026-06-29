import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add root and backend to system path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

# Load environment variables
env_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(env_path)

from app.config import settings
from app.services.qdrant_client import QdrantService
from supabase import create_client, Client
from fastembed import TextEmbedding

def main():
    print("==========================================================")
    print("PHASE 1 INGESTION VERIFICATION")
    print("==========================================================")

    # 1. Initialize Clients
    logger.info("Initializing Qdrant service...")
    qdrant = QdrantService()
    
    logger.info("Initializing Supabase client...")
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    # 2. Verify collection exists in Qdrant and get point count
    logger.info("Verifying Qdrant collection...")
    try:
        collection_info = qdrant.client.get_collection(qdrant.collection_name)
        points_count = collection_info.points_count
        status = collection_info.status
        vector_size = None
        distance = None
        # Handle different qdrant-client versions for vectors config
        params = collection_info.config.params
        if hasattr(params, "vectors") and params.vectors is not None:
            if hasattr(params.vectors, "size"):
                vector_size = params.vectors.size
                distance = params.vectors.distance
            elif isinstance(params.vectors, dict) and "size" in params.vectors:
                vector_size = params.vectors["size"]
                distance = params.vectors.get("distance")
        elif hasattr(params, "vector") and params.vector is not None:
            vector_size = params.vector.size
            distance = params.vector.distance

        print(f"\n[QDRANT] Collection: '{qdrant.collection_name}'")
        print(f"  - Status: {status}")
        print(f"  - Total Points (Ingested Tracks): {points_count}")
        if vector_size:
            print(f"  - Vector Dimensionality: {vector_size} (Expected: 384)")
            print(f"  - Distance Metric: {distance} (Expected: COSINE)")
        else:
            print("  - Vector configuration not found or could not be parsed.")
        
        if points_count >= 20000:
            print("  - PASS: Ingested points count is >= 20,000")
        else:
            print(f"  - WARNING: Ingested points count is {points_count} (Expected >= 20,000)")
            
        if vector_size == 384:
            print("  - PASS: Dimensionality matches 384 dimensions")
        elif vector_size:
            print(f"  - FAIL: Dimensionality is {vector_size} (Expected 384)")
        else:
            print("  - WARNING: Vector size not verified")
    except Exception as e:
        print(f"  - ERROR: Failed to retrieve Qdrant collection info: {e}")

    # 3. Verify Supabase track count and schema
    logger.info("Verifying Supabase tracks table...")
    try:
        res = supabase.table("tracks").select("id", count="exact").limit(5).execute()
        db_count = res.count
        
        print(f"\n[SUPABASE] Table: 'tracks'")
        print(f"  - Total Rows: {db_count}")
        
        if db_count == points_count:
            print(f"  - PASS: Supabase row count ({db_count}) matches Qdrant points count ({points_count})")
        else:
            print(f"  - WARNING: Mismatch! Supabase: {db_count}, Qdrant: {points_count}")
            
        # Sample metadata record
        if len(res.data) > 0:
            print("  - Sample record structure verified:")
            for k, v in res.data[0].items():
                print(f"    * {k}: {v}")
    except Exception as e:
        print(f"  - ERROR: Failed to retrieve Supabase tracks info: {e}")

    # 4. Verify descriptions generated
    logger.info("Retrieving sample descriptions...")
    try:
        res = supabase.table("tracks").select("track_name", "artist", "embedding_text").limit(3).execute()
        print("\n[DESCRIPTIONS] Sample generated descriptions:")
        for idx, row in enumerate(res.data):
            print(f"  {idx + 1}. Track: '{row['track_name']}' by {row['artist']}")
            print(f"     Description: \"{row['embedding_text']}\"")
    except Exception as e:
        print(f"  - ERROR: Failed to retrieve sample descriptions: {e}")

    # 5. Run test vector search query against Qdrant
    query_text = "sad and slow music"
    logger.info(f"Generating query embedding for: '{query_text}'...")
    try:
        model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
        query_vector = next(model.embed([query_text])).tolist()
        
        logger.info("Executing vector search query in Qdrant...")
        results = qdrant.search_similar_tracks(query_vector, limit=5)
        
        print(f"\n[SEARCH] Vector Search results for query: '{query_text}':")
        for idx, point in enumerate(results):
            payload = point.payload
            score = point.score
            print(f"  {idx + 1}. [Score: {score:.4f}] '{payload.get('track_name')}' by {payload.get('artist')}")
            print(f"     Genre: {payload.get('track_genre')}, Valence: {payload.get('valence')}, Energy: {payload.get('energy')}")
            
        if len(results) > 0 and results[0].score > 0.5:
            print("  - PASS: Vector search returned relevant tracks with similarity score > 0.5")
        else:
            print("  - WARNING: Vector search result score is lower than expected or returned no results.")
    except Exception as e:
        print(f"  - ERROR: Vector search failed: {e}")

    print("\n==========================================================")
    print("VERIFICATION COMPLETE")
    print("==========================================================")

if __name__ == "__main__":
    main()
