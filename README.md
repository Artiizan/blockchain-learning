# blockchain-learning

Creation of a Blockchain project to practice the full implementation of a blockchain with Proof of Work consesus. To Creation of a cryptocurrency on the blockchain. As well as building smart contracts.

## Blockchain Requirements
- Python 3.8.5 (64 bit)
- datetime
- hashlib
- json
- flask

## Blockchain HTTP Requests
Runs on port 5000

- GET : /get_chain
    Gets the current blocks in the chain as well as a length variable
- GET : /is_valid
    Checks the validity of the blockchain through the current and previous hash, iterates over the entire chain
- GET : /mine_block
    Creates a new block, difficulty is currently set to 4 leading zeros