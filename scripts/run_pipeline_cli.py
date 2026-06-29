import os
import sys
import argparse
import time
import json
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

from app.pipeline.orchestrator import PipelineOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Test run the Vibe-Checker AI pipeline via CLI.")
    parser.add_argument(
        "--prompt", 
        type=str, 
        default="Feeling low, need something that lifts me slowly",
        help="The emotional prompt to feed into the pipeline"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=None,
        help="Optional user UUID (simulates authenticated state if provided)"
    )
    parser.add_argument(
        "--ip",
        type=str,
        default="127.0.0.1",
        help="IP Address/fingerprint for anonymous rate limiting"
    )
    
    args = parser.parse_args()

    print("======================================================================")
    print("VIBE-CHECKER PIPELINE CLI RUNNER")
    print("======================================================================")
    print(f"Prompt: '{args.prompt}'")
    print(f"User ID: {args.user_id}")
    print(f"IP/Fingerprint: {args.ip}")
    print("======================================================================\n")

    try:
        # Initialize Orchestrator
        orchestrator = PipelineOrchestrator()
        
        # Execute pipeline
        start_time = time.time()
        vibe_queue = orchestrator.run(
            prompt=args.prompt,
            identifier=args.user_id if args.user_id else args.ip,
            is_authenticated=bool(args.user_id)
        )
        latency = (time.time() - start_time) * 1000

        # Output JSON result
        print("\nSUCCESS! Generated Vibe Queue JSON:")
        print(json.dumps(vibe_queue.model_dump(), indent=2))
        
        print("\n======================================================================")
        print(f"Execution Latency: {latency:.2f}ms")
        print(f"Total Tracks in Queue: {vibe_queue.queue_size}")
        print(f"Confidence Score: {vibe_queue.confidence}")
        print("======================================================================")
        
    except Exception as e:
        print(f"\nERROR: Pipeline execution failed!")
        print(f"Details: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
