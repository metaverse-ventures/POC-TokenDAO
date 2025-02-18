from base64 import b64decode
import logging
import base58
import requests


networks = {
    "eth": "https://mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
    "base": "https://base-mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
    "vana": "https://rpc.vana.org",
    "solana": "https://alien-side-emerald.solana-mainnet.quiknode.pro/a9c0f414bbd654569d77f8cfec805701a08b5f03",
}

TOTAL_SUPPLY_METHOD = "0x18160ddd"

def get_total_supply_evm(rpc_url, token_address):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": token_address, 
                "data": TOTAL_SUPPLY_METHOD, 
            },
            "latest", 
        ],
        "id": 1,
    }

    try:
        response = requests.post(rpc_url, json=payload, timeout=3)
        logging.info(f"response {response.text}")
        response.raise_for_status()
        result = response.json()

        total_supply_hex = result.get("result")
        if total_supply_hex == "0x":
            total_supply_hex = "0x0"
        if total_supply_hex:
            total_supply = int(total_supply_hex, 16)
            return total_supply
        else:
            return 0
    except Exception as e:
        logging.error("request error: %s", str(e), exc_info=True)
        return 0
    
def get_total_supply_solana(rpc_url, token_mint_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            token_mint_address, 
            {"encoding": "base64"},  
        ],
    }
    try:
        response = requests.post(rpc_url, json=payload, timeout=3)
        response.raise_for_status()
        result = response.json()

        account_info = result.get("result", {}).get("value")
        if account_info is None:
            logging.info( f"Error: Mint account {token_mint_address} not found.")
            return 0

        account_data = account_info["data"][0]
        decoded_data = b64decode(account_data)

        if len(decoded_data) < 82:
            logging.info("account not mint, invalid length")
            return 0
        
        
        decimals = decoded_data[44]
        is_initialized = decoded_data[45] == 1
        if not is_initialized or decimals <= 0 or decimals > 18:
            logging.info(f"account not mint, init {is_initialized} decimals {decimals}")
            return 0
        
        # Mint Account 
        mint_supply = int.from_bytes(decoded_data[36:44], "little") 
        # logging.info(f"sol mint, init {is_initialized} decimals {decimals}, supply {mint_supply}")
        return mint_supply
    except Exception as e:
        logging.error("request error: %s", str(e), exc_info=True)
        return 0
    
def is_valid_solana_address(address):
    if len(address) < 32 or len(address) > 44:
        return False
    try:

        decoded = base58.b58decode(address)
        if len(decoded) == 32:
            return True
        else:
            return False
        
    except Exception as e:
        return False
  

# Updated method to process the uniqueness with authenticity and ownership quality calculation
def calculate_token_metrics(unique_tokens, networks):
    results = []

    for token in unique_tokens:
        data_chain = token.get('chain', '').lower()
        data_contract = token.get('contract', '')
        data_reason = token.get('reason', '')
        print(f"Processing token {data_contract} on {data_chain} with reason: {data_reason}")
        # Ownership check
        # wallet_address_matches = config['wallet_address'] == wallet_address
        # ownership = 1 if wallet_address_matches else 0

        total_supply = 0

        if data_contract != "":
            if data_chain == "solana":
                if is_valid_solana_address(data_contract):
                    total_supply = get_total_supply_solana(networks[data_chain], data_contract)
            elif data_chain in ["eth", "base", "vana"]:
                if len(data_contract) == 42 and data_contract.lower().startswith("0x"):
                    total_supply = get_total_supply_evm(networks[data_chain], data_contract)

        logging.info(f"{data_contract} on {data_chain} supply {total_supply}")

        # Authenticity and Quality Calculation
        authenticity = 1 if total_supply > 0 else 0

        # Quality Calculation
        reason_length = len(data_reason.strip())
        if reason_length >= 30:
            quality = 1
        elif 15 <= reason_length < 29:
            quality = 0.5
        elif 6 <= reason_length < 14:
            quality = 0.1
        else:
            quality = 0

        # Save the results for each unique token
        results.append({
            "token": token,
            "authenticity": authenticity,
            "quality": quality
        })
    
    return results

def final_scores(unique_tokens):
    # return the average of the scores
    results = calculate_token_metrics(unique_tokens, networks)
    if not results:
        return 0, 0
    
    authenticity = sum(result['authenticity'] for result in results) / len(results)
    quality = sum(result['quality'] for result in results) / len(results)
    return authenticity, quality

# Example of how this would be executed
if __name__ == "__main__":
    # Assuming we have some example unique tokens
    unique_tokens = [
        {
            "chain": "Eth",
            "contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "reason": "We stand for: WINNING! Join my very special Trump Community."
        },
        {
            "chain": "Solana",
            "contract": "valid_sol_address",
            "reason": "New token released in celebration of a great win!"
        }
    ]
    
    networks = {
        "eth": "https://mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
        "base": "https://base-mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
        "vana": "https://rpc.vana.org",
        "solana": "https://alien-side-emerald.solana-mainnet.quiknode.pro/a9c0f414bbd654569d77f8cfec805701a08b5f03",
    }

    results = calculate_token_metrics( unique_tokens, networks)

    # Output the results
    for result in results:
        print(f"Token: {result['token']}")
        print(f"Ownership: {result['ownership']}, Authenticity: {result['authenticity']}, Quality: {result['quality']}")
