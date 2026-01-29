from web3 import Web3
import json

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
print(f"Connected: {w3.is_connected()}")

# Get first Ganache account (UPDATE this after test_ganache.py)
account = w3.eth.accounts[0]  # First account
print(f"Deploying from: {account}")

# Load compiled contract
with open('contracts/AuditLog.json') as f:
    contract_data = json.load(f)

# Create contract instance
AuditLog = w3.eth.contract(
    abi=contract_data['abi'],
    bytecode=contract_data['evm']['bytecode']['object']
)

# Get private key (CLICK FIRST ACCOUNT IN GANACHE → COPY PRIVATE KEY)
PRIVATE_KEY = '0x4308dc7d31c82c33d85e665e8b70155bb994e4c04eb025986bc2d780ef4c7c17'  # UPDATE THIS!

# Build transaction
tx = AuditLog.constructor().build_transaction({
    'from': account,
    'gas': 3000000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'nonce': w3.eth.get_transaction_count(account)
})

# Sign and send
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"🎉 Contract deployed at: {tx_receipt.contractAddress}")
print(f"📄 Tx hash: {tx_hash.hex()}")
print("\n📋 COPY THIS TO app.py:")
print(f"CONTRACT_ADDRESS = '{tx_receipt.contractAddress}'")
print(f"GANACHE_ACCOUNT = '{account}'")
