# Library Imports
import datetime
import hashlib
import json
from flask import Flask, jsonify


class Blockchain:

    def __init__(self):
        # Initialisation of the Blockchain as a list
        self.chain = []
        # Creation of Genesis block
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        # Define contents of our block
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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


# Creating Web Application
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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
    # Create a block
    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'Congratulations, block mined successfully!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200


# Get blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Check blockchain validity
@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {'is_valid': blockchain.validate_chain(blockchain.chain)}
    return jsonify(response), 200

# Running the App
app.run(host = '0.0.0.0', port = 5000)