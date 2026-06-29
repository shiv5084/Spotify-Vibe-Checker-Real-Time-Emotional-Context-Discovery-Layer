import os
import sys
import csv
import urllib.request
import logging
import time
import uuid
from dotenv import load_dotenv
from qdrant_client.http.models import PointStruct
from fastembed import TextEmbedding

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

DATASET_URL = "https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset/resolve/main/dataset.csv"
DATA_DIR = os.path.join(PROJECT_ROOT, "scripts", "data")
DATASET_PATH = os.path.join(DATA_DIR, "dataset.csv") 

# Set limit to ingest a subset for testing/MVP speed. None means ingest all (114k).
# We default to 15,000 for a fast, representative MVP run, but let it be overridden by env
INGESTION_LIMIT = int(os.getenv("INGESTION_LIMIT", "20000"))

def download_dataset():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if not os.path.exists(DATASET_PATH):
        logger.info(f"Downloading Spotify Tracks Dataset from: {DATASET_URL}")
        logger.info("This is a ~40MB download. Please wait...")
        
        def progress_hook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rDownloading... {percent}%")
            sys.stdout.flush()
            
        urllib.request.urlretrieve(DATASET_URL, DATASET_PATH, progress_hook)
        print("\nDownload finished.")
    else:
        logger.info(f"Dataset already exists at: {DATASET_PATH}")

def generate_description(row):
    """
    Generate a rich natural language description of a track based on its audio features.
    """
    artists = row['artists'].replace(';', ', ')
    track_name = row['track_name']
    genre = row['track_genre']
    
    # Emotional qualities (Valence & Energy)
    try:
        valence = float(row['valence'])
        energy = float(row['energy'])
        acousticness = float(row['acousticness'])
        danceability = float(row['danceability'])
        tempo = float(row['tempo'])
        instrumentalness = float(row['instrumentalness'])
    except ValueError:
        return None
    
    # Valence interpretation (emotional tone)
    if valence < 0.3:
        mood = "sad, melancholic, dark, and gloomy"
    elif valence < 0.6:
        mood = "bittersweet, reflective, neutral, and nostalgic"
    else:
        mood = "cheerful, happy, bright, and uplifting"
        
    # Energy interpretation
    if energy < 0.3:
        intensity = "calm, soft, peaceful, and low-energy"
    elif energy < 0.7:
        intensity = "moderate energy and pleasant"
    else:
        intensity = "high-energy, intense, loud, and active"
        
    # Acousticness
    acoustic_desc = "acoustic and organic" if acousticness > 0.5 else "electronic, electric, and synthesized"
    
    # Danceability
    dance_desc = "danceable, groovy, and rhythmic" if danceability > 0.6 else "subdued rhythm and steady"
    
    # Tempo (BPM)
    if tempo < 90:
        tempo_desc = "slow tempo"
    elif tempo < 130:
        tempo_desc = "moderate tempo"
    else:
        tempo_desc = "fast tempo"
        
    # Instrumentalness
    instr_desc = "instrumental track" if instrumentalness > 0.5 else "vocal-heavy track"
    
    description = (
        f"A {mood} {genre} song by {artists} titled '{track_name}'. "
        f"It features a {intensity} sound that is {acoustic_desc} with a {dance_desc} and {tempo_desc}. "
        f"It is an {instr_desc}."
    )
    return description

def clean_and_load_data(limit=None):
    logger.info(f"Loading and cleaning dataset. Limit set to: {limit}")
    
    tracks_to_process = []
    seen_ids = set()
    
    with open(DATASET_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            track_id = row.get('track_id')
            if not track_id or track_id in seen_ids:
                continue
                
            # Check for null values in key audio features
            try:
                float(row['valence'])
                float(row['energy'])
                float(row['acousticness'])
                float(row['danceability'])
                float(row['tempo'])
                float(row['instrumentalness'])
                float(row['loudness'])
                int(row['mode'])
                int(row['duration_ms'])
                int(row['popularity'])
            except (ValueError, TypeError):
                # Skip rows with malformed numeric data
                continue
                
            description = generate_description(row)
            if not description:
                continue
                
            row['description'] = description
            seen_ids.add(track_id)
            tracks_to_process.append(row)
            
            if limit and len(tracks_to_process) >= limit:
                break
                
    logger.info(f"Loaded and cleaned {len(tracks_to_process)} unique tracks.")
    return tracks_to_process

def main():
    # 1. Load Embedding Model first to prevent memory/pagefile exhaustion
    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)

    # 2. Download Spotify Dataset
    download_dataset()
    
    # 3. Clean and load tracks up to the limit
    tracks = clean_and_load_data(INGESTION_LIMIT)
    
    if not tracks:
        logger.error("No tracks loaded. Ingestion cancelled.")
        return
        
    # 4. Initialize Qdrant Client and Create Collection
    logger.info("Initializing Qdrant client...")
    qdrant = QdrantService()
    qdrant.create_collection_if_not_exists()
    
    # 5. Initialize Supabase Client
    logger.info("Initializing Supabase client...")
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    # 6. Process in batches (Embedding & Indexing)
    batch_size = 64
    total_tracks = len(tracks)
    logger.info(f"Starting ingestion of {total_tracks} tracks in batches of {batch_size}...")
    
    for idx in range(0, total_tracks, batch_size):
        batch = tracks[idx : idx + batch_size]
        logger.info(f"Processing batch {idx // batch_size + 1}/{(total_tracks + batch_size - 1) // batch_size} (Tracks {idx} to {min(idx + batch_size, total_tracks)})...")
        
        descriptions = [t['description'] for t in batch]
        
        # Generate Embeddings
        embeddings = [e.tolist() for e in model.embed(descriptions)]
        
        # Prepare Qdrant Points
        points = []
        for i, track in enumerate(batch):
            # Qdrant requires IDs to be unsigned ints or UUIDs; convert Spotify base62 ID to a deterministic UUID
            qdrant_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, track['track_id']))
            points.append(
                PointStruct(
                    id=qdrant_uuid,
                    vector=embeddings[i],
                    payload={
                        "track_id": track['track_id'],
                        "track_name": track['track_name'],
                        "artist": track['artists'].replace(';', ', '),
                        "album": track['album_name'],
                        "valence": float(track['valence']),
                        "energy": float(track['energy']),
                        "danceability": float(track['danceability']),
                        "tempo": float(track['tempo']),
                        "acousticness": float(track['acousticness']),
                        "instrumentalness": float(track['instrumentalness']),
                        "track_genre": track['track_genre']
                    }
                )
            )
            
        # Upsert into Qdrant
        qdrant.upsert_tracks(points)
        
        # Prepare Supabase Metadata Inserts
        supabase_data = []
        for i, track in enumerate(batch):
            supabase_data.append({
                "id": track['track_id'],
                "track_name": track['track_name'],
                "artist": track['artists'].replace(';', ', '),
                "album": track['album_name'],
                "valence": float(track['valence']),
                "energy": float(track['energy']),
                "danceability": float(track['danceability']),
                "tempo": float(track['tempo']),
                "acousticness": float(track['acousticness']),
                "instrumentalness": float(track['instrumentalness']),
                "loudness": float(track['loudness']),
                "speechiness": float(row := track.get('speechiness', 0.0)),
                "liveness": float(track.get('liveness', 0.0)),
                "mode": int(track['mode']),
                "duration_ms": int(track['duration_ms']),
                "popularity": int(track['popularity']),
                "track_genre": track['track_genre'],
                "embedding_text": track['description']
            })
            
        # Bulk Insert/Upsert into Supabase tracks table
        try:
            supabase.table("tracks").upsert(supabase_data).execute()
        except Exception as e:
            logger.error(f"Failed to insert metadata batch to Supabase: {e}")
            raise
            
        # Add rate-limiting delay between batches
        time.sleep(0.5)
            
    logger.info("Ingestion completed successfully!")

if __name__ == "__main__":
    main()
