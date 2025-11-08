import json
import argparse
import time
from pathlib import Path
import boto3



def list_pool_transactions(network, pool_address, max_results, client):
    txs = []
    next_token = None
    while True:
        kwargs = {
            "network": network,
            "address": pool_address,
            "maxResults": max_results
        } 
        if next_token: kwargs["nextToken"] = next_token

        resp = client.list_transactions(**kwargs)
        print(f"Response: {resp}")
        txs.extend(resp.get("transactions", []))
        next_token = resp.get("nextToken")
        print(f"Next token: {next_token}")
        if not next_token:
            break
    return txs
    
def list_events_for_tx(tx_hash, network, client, maxResults):
    events = []
    next_token = None

    while True:
        kwargs = {
            "network": network,
            "transactionHash": tx_hash,
            "maxResults": maxResults
        }
        if next_token: kwargs["nextToken"] = next_token

        resp = client.list_transaction_events(**kwargs)
        print(f"Response: {resp}")
        events.extend(resp.get("events", []))
        next_token = resp.get("nextToken")
        print(f"Next token: {next_token}")
        if not next_token:
            break
    return events

        
def main(network, client, pool_address, max_results):
    out_dir = Path("../data")

    print("Listing transactions...")
    txs = list_pool_transactions(network, pool_address, max_results, client)
    (out_dir / f"uni_v3_{pool_address}_transactions.json").write_text(json.dumps(txs, indent=2, default=str))
    print(f"Got {len(txs)} transactions")

    all_events = []
    for i, tx in enumerate(txs, 1):
        tx_hash = tx["transactionHash"]
        evs = list_events_for_tx(tx_hash, network, client, max_results)

        for e in evs:
            e["transactionHash"] = tx_hash
        all_events.extend(evs)

        if i % 50 ==0:
            print(f"{i}/{len(txs)} txs processed...")
            time.sleep(0.25)

    (out_dir / f"uni_v3_{pool_address}_events.json").write_text(json.dumps(all_events, indent=2, default=str))
    print(f"Saved {len(all_events)} events")



if __name__ == "__main__":
    # Args
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pool", default="0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8")
    parser.add_argument("--maxItems", default=250)
    parser.add_argument("-n", "--network", default="ETHEREUM_MAINNET")
    args = parser.parse_args()

    # client
    client = boto3.client("managedblockchain-query")
    main(args.network, client, args.pool, args.maxItems)


    
