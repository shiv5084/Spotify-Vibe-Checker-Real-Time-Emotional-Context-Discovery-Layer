import os
import sys
from dotenv import load_dotenv

# Add backend to path to load config
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

def main():
    print("======================================================================")
    print("Vibe-Checker Services Connection Verification")
    print("======================================================================")
    
    # Load .env file
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
        
    if os.path.exists(env_path):
        print(f"Loading environment variables from: {os.path.abspath(env_path)}")
        load_dotenv(env_path)
    else:
        print("WARNING: No .env file found. Testing using existing environment variables.")
        
    try:
        from app.config import settings
    except Exception as e:
        print(f"ERROR: Failed to load config.py. Is requirements.txt installed?")
        print(f"Details: {e}")
        return
        
    # 1. Test Groq
    print("\n1. Testing Groq API connection...")
    try:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        print("SUCCESS: Groq Connection Succeeded!")
        print(f"   Response: '{completion.choices[0].message.content.strip()}'")
    except Exception as e:
        print(f"ERROR: Groq Connection Failed: {e}")

    # 2. Test Qdrant
    print("\n2. Testing Qdrant Cloud connection...")
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        collections = client.get_collections()
        print("SUCCESS: Qdrant Connection Succeeded!")
        print(f"   Existing Collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"ERROR: Qdrant Connection Failed: {e}")

    # 3. Test Supabase
    print("\n3. Testing Supabase connection...")
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        # Test query profiles (should be empty but succeed)
        res = supabase.table("profiles").select("count", count="exact").limit(1).execute()
        print("SUCCESS: Supabase Connection Succeeded!")
        print(f"   Profiles count check: {res.count} profiles in table.")
    except Exception as e:
        print(f"ERROR: Supabase Connection Failed: {e}")

    # 4. Test Redis
    print("\n4. Testing Redis Connection...")
    try:
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        ping_result = r.ping()
        if ping_result:
            print("SUCCESS: Redis Connection Succeeded (Ping OK)!")
        else:
            print("ERROR: Redis Connection Failed (No Ping Response)")
    except Exception as e:
        print(f"ERROR: Redis Connection Failed: {e}")

    print("\n======================================================================")
    print("Verification Completed.")
    print("======================================================================")

if __name__ == "__main__":
    main()
