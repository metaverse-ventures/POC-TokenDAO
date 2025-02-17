import io
import json
import logging
import os
from typing import Dict, Any
import zipfile

import requests
import json
import hashlib
import base58
from base64 import b64decode

from my_proof.models.proof_response import ProofResponse

class Proof:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.proof_response = ProofResponse(dlp_id=config['dlp_id'])

    def generate(self) -> ProofResponse:
        """Generate proofs for all input files."""
        logging.info("Starting proof generation")

        # Iterate through files and calculate data validity
        account_email = ""
        data_chain = ""
        data_contract = ""
        data_reason = ""
        try:
            for input_filename in os.listdir(self.config['input_dir']):
                input_file = os.path.join(self.config['input_dir'], input_filename)
                if input_filename.lower() == 'decrypted_file.zip' or input_filename.lower() == 'token.json':
                    with open(input_file, 'r') as f:
                        input_data = json.load(f)
                        account_email = input_data.get('email', "")
                        data_chain = input_data.get('chain', "")
                        data_contract = input_data.get('contract', "")
                        data_reason = input_data.get('reason', "")
                        break
        except Exception as e:
            logging.error("parse json error: %s", str(e), exc_info=True)
        logging.info( "{} on {} supply {}".format(data_contract, data_chain, total_supply))
        

        self.proof_response.ownership = ownership
        self.proof_response.quality = quality
        self.proof_response.authenticity = authenticity
        self.proof_response.uniqueness = uniqueness

        # Calculate overall score and validity
        total_score = quality * (1 if uniqueness else 0.2) * ownership * authenticity
        self.proof_response.score = total_score
        self.proof_response.valid = ownership and total_score >= 0

        # Additional (public) properties to include in the proof about the data
        self.proof_response.attributes = {
            'total_score': total_score,
            'score_threshold': quality,
            'email_verified': email_matches,
        }

        # Additional metadata about the proof, written onchain
        self.proof_response.metadata = {
            'dlp_id': self.config['dlp_id'],
        }

        return self.proof_response


def check_hash_repeat(rpc_url, hash):
    payload = {
        "hash": hash,
    }
    try:
        response = requests.post(rpc_url, json=payload, timeout=3)
        response.raise_for_status()
        result = response.json()

        result_data = bool(result.get("data", False))

        return not result_data
    
    except Exception as e:
        logging.error("request error: %s", str(e), exc_info=True)
        return True