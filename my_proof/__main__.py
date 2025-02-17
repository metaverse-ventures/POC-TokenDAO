import json
import logging
import os
import sys
import traceback
import zipfile
from typing import Dict, Any

from my_proof.proof import Proof

# Default to 'production' if NODE_ENV is not set
environment = os.environ.get('NODE_ENV', 'production')

# Set the input and output directories based on the environment
INPUT_DIR = './demo/input' if environment == 'development' else '/input'
OUTPUT_DIR = './demo/output' if environment == 'development' else '/output'
SEALED_DIR = './demo/sealed' if environment == 'development' else '/sealed'

logging.basicConfig(level=logging.INFO, format='%(message)s')


def load_config() -> Dict[str, Any]:
    """Load proof configuration from environment variables."""
    config = {
        'dlp_id': 24,
        'input_dir': INPUT_DIR,
        'user_email': os.environ.get('USER_EMAIL', None) or "dev@test.com",
    }
    logging.info(f"Using config: {json.dumps(config, indent=2)}")
    return config


def run() -> None:
    """Generate proofs for all input files."""
    config = load_config()
    input_files_exist = os.path.isdir(INPUT_DIR) and bool(os.listdir(INPUT_DIR))

    if not input_files_exist:
        raise FileNotFoundError(f"No input files found in {INPUT_DIR}")

    proof = Proof(config)
    proof_response = proof.generate()

    output_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(output_path, 'w') as f:
        json.dump(proof_response.dict(), f, indent=2)
    logging.info(f"Proof generation complete: {proof_response}")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logging.error(f"Error during proof generation: {e}")
        traceback.print_exc()
        sys.exit(1)
