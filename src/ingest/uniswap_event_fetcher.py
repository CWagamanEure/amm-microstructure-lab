from dotenv import load_dotenv 
import os
import json
from pathlib import Path
from web3 import Web3
import argparse
load_dotenv()

def event_topic(signature):
    return Web3.to_hex(Web3.keccak(text=signature))

def fetch_events(topic0, event_obj, start_block, end_block, pool_address, w3, step=5_000):
    events = []
    for from_block in range(start_block, end_block +1, step):
        to_block = min(from_block + step -1, end_block)
        logs = w3.eth.get_logs({
            "fromBlock": from_block,
            "toBlock": to_block,
            "address": pool_address,
            "topics": [topic0],
        })
        print(logs)
        for log in logs:
            print(log)
            decoded = event_obj.process_log(log)
            events.append({
                "block_number": decoded.blockNumber,
                "tx_hash": decoded.transactionHash.hex(),
                "log_index": decoded.logIndex,
                **decoded["args"]
            })
    return events


if __name__ == "__main__":
    RPC_URL = os.getenv("RPC_URL")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    assert w3.is_connected(), "Failed to connect to AMB Access node"

    default_end = w3.eth.block_number
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--poolAddress", default="0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8")
    parser.add_argument("-s", "--startBlock", default=1, type=int)
    parser.add_argument("-e", "--endBlock", default=default_end, type=int)
    args= parser.parse_args()
    POOL_ADDR = Web3.to_checksum_address(args.poolAddress)

    with open("../../data/abis/UniswapV3Pool.json") as f:
        artifact = json.load(f)
    pool_abi = artifact["abi"] if "abi" in artifact else artifact

    pool = w3.eth.contract(address=POOL_ADDR, abi=pool_abi)

    swap_topic0 = event_topic("Swap(address,address,int256,int256,uint160,uint128,int24)")
    mint_topic0 = event_topic("Mint(address,address,int24,int24,uint128,uint256,uint256)")
    burn_topic0 = event_topic("Burn(address,int24,int24,uint128,uint256,uint256)")

    swaps = fetch_events(swap_topic0, pool.events.Swap(), args.startBlock, args.endBlock, POOL_ADDR, w3)
    mints = fetch_events(mint_topic0, pool.events.Mint(), args.startBlock, args.endBlock, POOL_ADDR, w3)
    burns = fetch_events(burn_topic0, pool.events.Burn(), args.startBlock, args.endBlock, POOL_ADDR, w3)

    Path(f"../../data/raw/{POOL_ADDR}_swaps.json").write_text(json.dumps(swaps))
    Path(f"../../data/raw/{POOL_ADDR}_mints.json").write_text(json.dumps(mints))
    Path(f"../../data/raw/{POOL_ADDR}_burns.json").write_text(json.dumps(burns))






