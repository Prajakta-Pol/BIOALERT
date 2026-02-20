from web3 import Web3
#from dotenv import load_dotenv
import os
import hashlib

# Use a simple hash for data
def hash_data(data: str):
    return hashlib.sha256(data.encode()).hexdigest()

# Store the hash on-chain (test method)
def store_hash_on_chain(data_hash):
    try:
        nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)
        tx = {
            "nonce": nonce,
            "to": PUBLIC_ADDRESS,   # self-transfer (just to record)
            "value": 0,
            "gas": 200000,
            "gasPrice": w3.to_wei("30", "gwei"),
            "data": data_hash.encode("utf-8")[:68]  # limited size for demo
        }

        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print("✅ Hash stored! Tx Hash:", w3.to_hex(tx_hash))
        return w3.to_hex(tx_hash)

    except Exception as e:
        print("⚠️ Blockchain error:", e)
        return None