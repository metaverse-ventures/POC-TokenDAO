import json
import logging
import os
from typing import Dict, Any
import json

from my_proof.proof_of_ownership import verify_ownership
from my_proof.proof_of_uniqueness import uniqueness_details
from my_proof.proof_of_quality_n_authenticity import final_scores
from my_proof.models.proof_response import ProofResponse

class Proof:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.proof_response = ProofResponse(dlp_id=config['dlp_id'])
        self.wallet_address = ""
    
    def read_author_from_file(self, file_path: str):
        """
        Read parameters from a text file.

        :param file_path: Path to the text file
        :return: Tuple containing author, signature, and random_string
        """
        params = {}
        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split(": ", 1)
                params[key] = value
        return params["author"]

    def generate(self) -> ProofResponse:
        """Generate proofs for all input files."""
        logging.info("Starting proof generation")

        # Read the wallet address from the first .txt file in the input directory
        txt_files = [f for f in os.listdir(self.config['input_dir']) if f.endswith('.txt')]
        if txt_files:
            self.wallet_address = self.read_author_from_file(os.path.join(self.config['input_dir'], txt_files[0])).lower()
            logging.info(f"Wallet Address {self.wallet_address}")

        uniqueness_details_ = uniqueness_details(self.wallet_address, self.config['input_dir'] )
        unique_tokens = uniqueness_details_.get("unique_json_data", [])
        logging.info(f" Count of Unique tokens from proof.py: {len(unique_tokens)}")

        uniqueness_score = uniqueness_details_.get("uniqueness_score", 0.0)
        authenticity_score, quality_score = final_scores(unique_tokens)
        # Calculate uniqueness with authenticity and ownership quality

        ownership_score = verify_ownership(self.config['input_dir'])
        self.proof_response.ownership = ownership_score
        self.proof_response.quality = quality_score
        self.proof_response.authenticity = authenticity_score
        self.proof_response.uniqueness = uniqueness_score

        self.proof_response.score = self.calculate_final_score(len(unique_tokens))
        self.proof_response.valid = True

        # Additional metadata about the proof, written onchain
        self.proof_response.metadata = {
            'dlp_id': self.config['dlp_id'],
        }

        return self.proof_response
    
    def calculate_final_score(self, unique_token_count) -> float:
        max_rewards = os.environ.get("MAX_TOKEN_REWARD",100)
        reward_per_token = os.environ.get("REWARD_PER_TOKEN",1)
        score = (unique_token_count * reward_per_token) / max_rewards
        return score
