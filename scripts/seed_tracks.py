import os
import sys
import csv
import urllib.request
import logging
import time
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
from supabase import create_client, Client

DATASET_URL = "https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset/resolve/main/dataset.csv"
DATA_DIR = os.path.join(PROJECT_ROOT, "scripts", "data")
DATASET_PATH = os.path.join(DATA_DIR, "dataset.csv")

# Set limit to seed a subset for testing/MVP speed
INGESTION_LIMIT = int(os.getenv("INGESTION_LIMIT", "15000"))

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
    logger.info(f"Loading and cleaning dataset for seeding. Limit set to: {limit}")
    
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
                continue
                
            description = generate_description(row)
            if not description:
                continue
                
            row['description'] = description
            seen_ids.add(track_id)
            tracks_to_process.append(row)
            
            if limit and len(tracks_to_process) >= limit:
                break
                
    logger.info(f"Loaded and cleaned {len(tracks_to_process)} unique tracks for seeding.")
    return tracks_to_process

def main():
    # 1. Download Spotify Dataset if needed
    download_dataset()
    
    # 2. Clean and load tracks up to the limit
    tracks = clean_and_load_data(INGESTION_LIMIT)
    
    if not tracks:
        logger.error("No tracks loaded. Seeding cancelled.")
        return

    # 3. Initialize Supabase Client
    logger.info("Initializing Supabase client...")
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    # 4. Batch seed Supabase metadata
    batch_size = 100
    total_tracks = len(tracks)
    logger.info(f"Starting seeding of {total_tracks} tracks to PostgreSQL in batches of {batch_size}...")
    
    success_count = 0
    failure_count = 0
    start_time = time.time()
    
    for idx in range(0, total_tracks, batch_size):
        batch = tracks[idx : idx + batch_size]
        
        supabase_data = []
        for track in batch:
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
                "speechiness": float(track.get('speechiness', 0.0)),
                "liveness": float(track.get('liveness', 0.0)),
                "mode": int(track['mode']),
                "duration_ms": int(track['duration_ms']),
                "popularity": int(track['popularity']),
                "track_genre": track['track_genre'],
                "embedding_text": track['description']
            })
            
        try:
            supabase.table("tracks").upsert(supabase_data).execute()
            success_count += len(batch)
            logger.info(f"Successfully seeded batch {idx // batch_size + 1}: seeded {success_count}/{total_tracks}")
        except Exception as e:
            logger.error(f"Failed to seed batch to Supabase: {e}")
            failure_count += len(batch)
            
        # Small delay to respect API limits
        time.sleep(0.1)
        
    duration = time.time() - start_time
    logger.info("==========================================================")
    logger.info(f"Seeding completed in {duration:.2f} seconds.")
    logger.info(f"Total processed: {total_tracks}")
    logger.info(f"Successfully seeded: {success_count}")
    logger.info(f"Failed: {failure_count}")
    logger.info("==========================================================")

if __name__ == "__main__":
    main()
