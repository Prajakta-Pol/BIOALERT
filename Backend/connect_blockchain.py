from web3 import Web3

# Replace this with your own Alchemy RPC URL
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/zKH4atCaQtUPM9Upe-ZaV"

# Connect to the Polygon Amoy testnet
web3 = Web3(Web3.HTTPProvider(alchemy_url))

if web3.is_connected():
    print("✅ Connected to Polygon Amoy testnet!")
    print("Current block number:", web3.eth.block_number)
else:
    print("❌ Connection failed.")
