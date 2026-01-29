from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))

# Test connection
print("=== Ganache Connection Test ===")
print(f"Connected: {w3.is_connected()}")  # Should be True

print("\n=== Ganache Accounts ===")
print(w3.eth.accounts)  # Should show 10 accounts like ['0x...', '0x...']

print("\n=== Block Number ===")
print(w3.eth.block_number)  # Should show a number like 1

print("\n=== Ganache Ready! ===")
