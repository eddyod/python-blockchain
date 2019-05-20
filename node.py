from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from argparse import ArgumentParser

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('views', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('views', 'network.html')




@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        status = 201
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
    else:
        response = {
            'message': 'Saving keys failed.'
        }
        status = 500
    return jsonify(response), status



@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        status = 201
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
    else:
        response = {
            'message': 'Loading keys failed.'
        }
        status = 500
    return jsonify(response), status

@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Getting balance worked.',
            'wallet_set_up': balance
        }
        status = 201
    else:
        response = {
            'message': 'Getting balance failed.',
            'wallet_set_up': wallet.public_key != None
        }
        status = 500
    return jsonify(response), status

@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set.'
        }
        return jsonify(response), 400

    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400

    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Missing fields in data.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Creating transaction worked.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        status = 201
    else:
        response = {
            'message': 'Creating transaction failed.'
        }
        status = 400
    return jsonify(response), status


@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 201





@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.get_chain()
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 201

@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached for node.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node data in response.'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added OK.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node>', methods=['DELETE'])
def remove_node(node):
    
    if node == '' or node == None:
        response = {
            'message': 'No data attached for node removal.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node)
    response = {
        'message': 'Node removed OK.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)


