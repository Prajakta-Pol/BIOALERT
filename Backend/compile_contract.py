import solcx
import json

# Install Solidity compiler
solcx.install_solc('0.8.19')

# Read your AuditLog.sol (make sure contracts/AuditLog.sol exists)
with open('contracts/AuditLog.sol', 'r') as f:
    source_code = f.read()

# Compile
compiled_sol = solcx.compile_standard({
    "language": "Solidity",
    "sources": {"AuditLog.sol": {"content": source_code}},
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
})

# Save compiled contract
contract_interface = compiled_sol['contracts']['AuditLog.sol']['AuditLog']

with open('contracts/AuditLog.json', 'w') as f:
    json.dump(contract_interface, f, indent=2)

print("✅ AuditLog.json created!")
