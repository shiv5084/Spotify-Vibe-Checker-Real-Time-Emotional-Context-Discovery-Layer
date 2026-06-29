import os
import sys
import argparse
import json
from dotenv import load_dotenv

# Add root and backend to system path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "backend"))

# Load environment variables
env_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(env_path)

from app.services.groq_client import GroqClient

def main():
    parser = argparse.ArgumentParser(description="Test emotional profile JSON extraction directly from Groq.")
    parser.add_argument(
        "--prompt", 
        type=str, 
        default="Feeling low, need something that lifts me slowly",
        help="The emotional prompt to test"
    )
    args = parser.parse_args()

    print("==========================================================")
    print(f"QUERYING GROQ FOR PROMPT: '{args.prompt}'")
    print("==========================================================\n")

    try:
        # Initialize GroqClient
        groq_client = GroqClient()
        
        # Run emotion extraction
        profile_json = groq_client.extract_emotional_profile(args.prompt)
        
        print("EXACT JSON RESPONSE FROM LLM:")
        print(json.dumps(profile_json, indent=2))
        
    except Exception as e:
        print(f"\nERROR: Extraction failed!")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()
