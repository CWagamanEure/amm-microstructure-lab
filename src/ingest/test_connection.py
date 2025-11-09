from dotenv import load_dotenv
import os
from web3 import Web3

load_dotenv()
rpc = os.getenv("RPC_URL")
print("RPC_URL:", repr(rpc))
w3 = Web3(Web3.HTTPProvider(rpc))
print("is_connected:", w3.is_connected())
print("blockNumber:", w3.eth.block_number if w3.is_connected() else None)
