from functools import reduce
from collections import OrderedDict
from hash_util import hash_string_256, hash_block
import json


MINING_REWARD = 10
GENESIS_BLOCK = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
    }
blockchain = [GENESIS_BLOCK]
open_transactions = []
owner = 'Fast Eddy'
participants = {owner}


def save_data():
    with open('blockchain.txt', mode='w') as f:
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(open_transactions))


def load_data():
    with open('blockchain.txt', mode='r') as f:
        file_contents = f.readlines()
        global blockchain
        global open_transactions
        blockchain = json.loads(file_contents[0][:-1])
        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash': block['previous_hash'],
                'index': block['index'],
                'proof': block['proof'],
                'transactions': [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
                }
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain

        open_transactions = json.loads(file_contents[1])
        updated_blockchain = []
        for tx in open_transactions:
            updated_block = OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
            updated_blockchain.append(updated_block)
        open_transactions = updated_blockchain



load_data()

def get_last_blockchain_value():
    """ Returns the last value of the current blockchain """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def print_blockchain_elements():
    #  output the blockchain list to the console
    for block in blockchain:
        print('Block:', block)
    else:
        print('-' * 20)


def get_user_choice():
    user_input = input('Your choice:')
    return user_input


def get_transaction_value():
    tx_recipient = input('Enter the recipient: ')
    tx_amount = float(input('Your transaction amount: '))
    return (tx_recipient, tx_amount)


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Add a value to the block
     Arguments:
        : sender: person
        : recipient: person
        : amount: how much
    """
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = OrderedDict(
            [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)]
        )

    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
        }
    blockchain.append(block)
    return True


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    amount_sent = 0
    amount_received = 0
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions
                      if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                   if len(tx_amt) > 0
                                   else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                       if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    return amount_received - amount_sent


def verify_block():
    """ Verify the current blockchain and return True if valid"""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
    return True


def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work invalid')
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('a: Add a new transaction value')
    print('m: Mine a block')
    print('p: Print the blockchain')
    print('h: Manipulate the chain')
    print('o: Output participants')
    print('c: Check transaction value')
    print('q: quit')
    user_choice = get_user_choice()
    if user_choice == 'a':
        tx_recipient, tx_amount = get_transaction_value()
        if add_transaction(tx_recipient, owner, tx_amount):
            print('Added transaction')
        else:
            print('Failed transaction')
    elif user_choice == 'p':
        print_blockchain_elements()
    elif user_choice == 'm':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{
                    'sender': 'Chris',
                    'recipient': 'JJJ',
                    'amount': 100}]
                }
    elif user_choice == 'o':
        print(participants)
    elif user_choice == 'c':
        if verify_transactions():
            print('All tranactions are valid')
        else:
            print('Contains invalid transactions')
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, choose a or p or q to quit.')

    if not verify_block():
        print_blockchain_elements()
        print('Invalid blockchain')
        waiting_for_input = False
    print('Balance of {}: {:6.2f}'.format(owner, get_balance(owner)))
else:
    print('Left while.')

print('Done.')
