from solcx import compile_standard
import json
from web3 import Web3
from dotenv import load_dotenv
import os


load_dotenv()
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    print(simple_storage_file)

# Compile Our Solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get Bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
print(bytecode)
print("***********************")
# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
print(abi)

# for connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
#w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
#w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

print("Is connected:", w3.is_connected())
chain_id = 1337
my_address = "0x8cbe573748eEe49c31A453AADaEFd0467bec6e5d"
#my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"

private_key = os.getenv("PRIVATE_KEY")
print(private_key)
# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
print(SimpleStorage)

# get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)
print(nonce)
# 1.Build a transaction
# 2.Sign a transaction
# 3.send a transaction

transaction = SimpleStorage.constructor().build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)


signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send this Signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Deployed ")
# Practical 10
# Working with contract ,You need:
# contract ABI
# Contract Address

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change
# initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")

store_transaction = simple_storage.functions.store(15).build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("updated !")
print(simple_storage.functions.retrieve().call())
