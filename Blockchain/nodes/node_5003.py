# Library Imports
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:

    def __init__(self):
        # Initialisation of the Blockchain as a list
        self.chain = []
        # Creation of Genesis block
        self.create_block(proof=1, previous_hash='0')
        # Initialisation of 'mempool' for transactions
        self.mempool = []
        # Initialisation of nodes as a set
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        # Define contents of our block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            # We are taking all transactions from the mempool in one go for simplicity
            'transactions': self.mempool
        }
        self.mempool = []
        # Add the block to the chain
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while (check_proof == False):
            # Definition of problem for miners to solve
            # Simple non-symetrical operation
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            # Possible to increase difficulty programmatically by increasing the number of leading zeros
            if (hash_operation[0:4] == '0000'):
                check_proof = True
            else:
                # Increment proof to give miner another chance
                new_proof += 1
        return new_proof

    def validate_chain(self, chain):
        # Initialise variables
        previous_block = chain[0]
        block_index = 1

        while (block_index < len(chain)):
            current_block = chain[block_index]

            # Checking hash of previous block is valid
            if (current_block['previous_hash'] != self.hash_block(previous_block)):
                return False

            # Checking that the proofs are correct
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']
            hash_operation = hashlib.sha256(
                str(current_proof**2 - previous_proof**2).encode()).hexdigest()
            if (hash_operation[0:4] != '0000'):
                return False

            previous_block = current_block
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):
        self.mempool.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        # As we are adding all transactions to the next block, we will return the index of the block this transaction will be in
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_address = urlparse(address)
        self.nodes.add(parsed_address.netloc)

    def replace_chain(self):
        # Initialise variables
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for node in network:
            # Send request to Node to get blockchain on that node as well as it's length
            response = requests.get(f'http://{node}/get_chain')
            if (response.status_code == 200):
                length = response.json()['length']
                chain = response.json()['chain']

                # Checks length of chain and validity of chain
                if (length > max_length and self.is_valid(chain)):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        else:
            return False


# Creating Web Application
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creation of uuid address for node on main port
node_address = str(uuid4()).replace('-', '')

# Instantiation of Blockchain Class
blockchain = Blockchain()


## HTTP Functions ##

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    # Instantiate variables of Previous Block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    previous_hash = blockchain.hash_block(previous_block)

    # Mine proof of current block
    proof = blockchain.proof_of_work(previous_proof)

    # Adds transaction with static variables for receiver and amount
    blockchain.add_transaction(node_address, 'User 3', 10)

    # Create a block
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'Congratulations, block mined successfully!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions'],
    }
    return jsonify(response), 200


# Get blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


# Check blockchain validity
@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {'is_valid': blockchain.validate_chain(blockchain.chain)}
    return jsonify(response), 200


# Adding transaction to the Mempool
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()

    # Checking that all data is present in the request
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Please ensure that you include the sender, receiver and amount in the request.', 400

    # Creation of transaction
    block_index = blockchain.add_transaction(
        json['sender'], json['receiver'], json['amount'])

    response = {
        'message': f'Success! Your transaction will be added to block {block_index}'}
    return jsonify(response), 201


# Connecting new node to further decentralise the blockchain
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()

    # Get addresses of nodes
    nodes = json.get('nodes')
    if (nodes is None):
        return "No nodes", 400

    # Add nodes
    for node in nodes:
        blockchain.add_node(node)

    response = {
        'message': 'All nodes connected.',
        'network_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 200


# Replacing the chain with the longest chain in the network
@app.route('/replace_chain', methods=['GET'])
def is_valid():
    response = {
        'chain_replaced': blockchain.replace_chain(),
        'chain': blockchain.chain
    }
    return jsonify(response), 200


# Running the App
app.run(host='0.0.0.0', port=5003)
