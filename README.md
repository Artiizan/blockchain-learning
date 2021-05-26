# blockchain-learning

Creation of a Blockchain project to practice the full implementation of a blockchain with Proof of Work consesus. To Creation of a cryptocurrency on the blockchain. As well as building smart contracts.

## Blockchain Requirements
- Python 3.8.5 (64 bit)
- datetime
- hashlib
- json
- flask
- requests
- uuid
- urllib.parse

## Blockchain HTTP Requests

- GET : /get_chain
    Gets the current blocks in the chain as well as a length variable
- GET : /is_valid
    Checks the validity of the blockchain through the current and previous hash, iterates over the entire chain
- GET : /mine_block
    Creates a new block, difficulty is currently set to 4 leading zeros. This also includes the transactions from the mempool and pays the miner for their work
- POST : /add_transaction
    Adds a transaction to the mempool, and returns the index of the block that the transaction will be included in. This mempool is currently node specific
- POST : /connect_node
    Links other nodes to the node that this command is run on. This allows execution of the /replace_chain command
- GET : /replace_chain
    Checks which node has the longest and valid chain, then proceeds to replace this node with that chain if it is longer. Chain specific command