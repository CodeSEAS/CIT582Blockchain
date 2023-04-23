from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import math
import sys
import traceback

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

""" Pre-defined methods (do not need to change) """

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()

def connect_to_blockchains():
    try:
        # If g.acl has not been defined yet, then trying to query it fails
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True
    
    try:
        if acl_flag or not g.acl.status():
            # Define Algorand client for the application
            g.acl = connect_to_algo()
    except Exception as e:
        print("Trying to connect to algorand client again")
        print(traceback.format_exc())
        g.acl = connect_to_algo()
    
    try:
        icl_flag = False
        g.icl
    except AttributeError as ae:
        icl_flag = True
    
    try:
        if icl_flag or not g.icl.health():
            # Define the index client
            g.icl = connect_to_algo(connection_type='indexer')
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type='indexer')

        
    try:
        w3_flag = False
        g.w3
    except AttributeError as ae:
        w3_flag = True
    
    try:
        if w3_flag or not g.w3.isConnected():
            g.w3 = connect_to_eth()
    except Exception as e:
        print("Trying to connect to web3 again")
        print(traceback.format_exc())
        g.w3 = connect_to_eth()
        
""" End of pre-defined methods """
        
""" Helper Methods (skeleton code for you to implement) """

def log_message(message_dict):
    from datetime import datetime
    msg = json.dumps(message_dict)

    # TODO: Add message to the Log table
    g.session.add(Log(logtime=datetime.now(), message=msg))
    g.session.commit()
    return

def get_algo_keys():
    
    # TODO: Generate or read (using the mnemonic secret) 
    # the algorand public/private keys
    import algosdk as ak

    algo_sk, algo_pk = ak.account.generate_account()
    print(f"get_algo_keys sk: {algo_sk}, pk: {algo_pk}")

    return algo_sk, algo_pk


def get_eth_keys(filename = "eth_mnemonic.txt"):
    # w3 = Web3()
    # from web3 import Web3
    
    # TODO: Generate or read (using the mnemonic secret) 
    # the ethereum public/private keys
    # ALCHEMY_API_KEY = "kBQFL6fReQL7Rafl6CSLVbtB9nCRfszA"
    # w3 = Web3(Web3.HTTPProvider(f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}')) 
    # account = w3.eth.account.create()
    # eth_sk = account.key.hex()
    # eth_pk = account.address
    eth_sk = b'N\xa3cW\xb4\xdc10\x84\xf8\x05\xed\x98\xef\xf4\xfe\xa8Z\xfa\xe1\xc5\xf3\x05\xe3\xebM\xc5_7\xf3s\x04'
    eth_pk = '0xEBE97c09Fa8672f435f88c58fFe08CE495Bb34eF'
    print(f"get_eth_keys sk: {eth_sk}, pk: {eth_pk}")
    return eth_sk, eth_pk
  
def fill_order(order, txes=[]):
    # TODO: 
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!
    
    session = g.session
    # sender_pk = order.sender_pk
    # receiver_pk = order.receiver_pk
    # buy_currency = order.buy_currency
    # sell_currency = order.sell_currency
    # buy_amount = order.buy_amount
    # sell_amount = order.sell_amount
    new_inserted_order = Order(sender_pk = order['sender_pk'], 
                               receiver_pk = order['receiver_pk'], 
                               buy_currency = order['buy_currency'], 
                               sell_currency = order['sell_currency'], 
                               buy_amount = order['buy_amount'], 
                               sell_amount = order['sell_amount'])
    # new_inserted_order = Order(sender_pk=sender_pk, receiver_pk=receiver_pk, buy_currency=buy_currency,
    #                    sell_currency=sell_currency, buy_amount=buy_amount, sell_amount=sell_amount)
    session.add(new_inserted_order)
    session.commit()

    for existing_order in session.query(Order).filter(Order.creator == None).all():
        if existing_order.filled is not None:
            continue
        if existing_order.sell_currency != new_inserted_order.buy_currency:
            continue
        if existing_order.buy_currency != new_inserted_order.sell_currency:
            continue
        if existing_order.sell_amount / existing_order.buy_amount < new_inserted_order.buy_amount / new_inserted_order.sell_amount:
            continue
        new_inserted_order.filled = datetime.now()
        existing_order.filled = datetime.now()
        new_inserted_order.counterparty_id = existing_order.id
        existing_order.counterparty_id = new_inserted_order.id
        session.commit()

        if new_inserted_order.sell_amount < existing_order.buy_amount:
            new_buy_amount = existing_order.buy_amount - new_inserted_order.sell_amount
            new_sell_amount = (existing_order.buy_amount - new_inserted_order.sell_amount) * existing_order.sell_amount / existing_order.buy_amount
            modified_order = Order(sender_pk = existing_order.sender_pk, 
                               receiver_pk = existing_order.receiver_pk, 
                               buy_currency = existing_order.buy_currency, 
                               sell_currency =  existing_order.sell_currency, 
                               buy_amount = new_buy_amount, 
                               sell_amount = new_sell_amount,
                               creator_id = existing_order.id)
            session.add(modified_order)
            session.commit()
        elif new_inserted_order.sell_amount > existing_order.buy_amount:
            new_buy_amount = (new_inserted_order.sell_amount - existing_order.buy_amount) * new_inserted_order.buy_amount/ new_inserted_order.sell_amount
            new_sell_amount = new_inserted_order.sell_amount - existing_order.buy_amount
            modified_order = Order(sender_pk = order['sender_pk'], 
                               receiver_pk = order['receiver_pk'], 
                               buy_currency = order['buy_currency'], 
                               sell_currency = order['sell_currency'], 
                               buy_amount = new_buy_amount, 
                               sell_amount = new_sell_amount,
                               creator_id = new_inserted_order.id)
            session.add(modified_order)
            session.commit()    
        break
    return  
  
def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print( f"Trying to execute {len(txes)} transactions" )
    print( f"IDs = {[tx['order_id'] for tx in txes]}" )
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()
    
    if not all( tx['platform'] in ["Algorand","Ethereum"] for tx in txes ):
        print( "Error: execute_txes got an invalid platform!" )
        print( tx['platform'] for tx in txes )

    algo_txes = [tx for tx in txes if tx['platform'] == "Algorand" ]
    eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum" ]

    # TODO: 
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table

    for order in algo_txes:
        txe = TX(platform="Ethereum", receiver_pk=order['receiver_pk'],
                 order_id=order['order_id'] )
        txe.tx_id = send_tokens_algo(connect_to_algo(), algo_sk, order)
        g.session.add(txe)
        g.session.commit()

    for order in eth_txes:
        txe = TX(platform="Algorand", receiver_pk=order['receiver_pk'],
                 order_id=order['order_id'])
        txe.tx_id = send_tokens_eth(connect_to_eth(), eth_sk, order)
        g.session.add(txe)
        g.session.commit()

""" End of Helper methods"""
  
@app.route('/address', methods=['POST'])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        if 'platform' not in content.keys():
            print( f"Error: no platform provided" )
            return jsonify( "Error: no platform provided" )
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print( f"Error: {content['platform']} is an invalid platform" )
            return jsonify( f"Error: invalid platform provided: {content['platform']}"  )
        
        if content['platform'] == "Ethereum":
            #Your code here
            eth_sk, eth_pk = get_eth_keys()
            return jsonify( eth_pk )
        if content['platform'] == "Algorand":
            #Your code here
            algo_sk, algo_pk = get_algo_keys()
            return jsonify( algo_pk )
        

def check_sig(payloads, request_sig):
    request_sig = request_sig  
    payload_platform = payloads['platform']  
    payload_pk = payloads['pk'] 
    payload_message = json.dumps(payloads)

    if payload_platform == 'Ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text = payload_message)
        eth_pk = eth_account.Account.recover_message(eth_encoded_msg, signature = request_sig)

        if payload_pk == eth_pk:
            result = True
        else: 
            result = False
    
    elif payload_platform == 'Algorand':
        if algosdk.util.verify_bytes(payload_message.encode('utf-8'), request_sig, payload_pk):
            result = True
        else: 
            result = False
    else:
        result = False
    return result


@app.route('/trade', methods=['POST'])
def trade():
    print( "In trade", file=sys.stderr )
    connect_to_blockchains()
    # get_keys()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
        fields = [ "sig", "payload" ]
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )
        
        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )
        
        # Your code here
        
        # 1. Check the signature
        
        # 2. Add the order to the table
        
        # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)

        # 3b. Fill the order (as in Exchange Server II) if the order is valid
        
        # 4. Execute the transactions
        
        # If all goes well, return jsonify(True). else return jsonify(False)
        # return jsonify(True)

        res = check_sig(content['payload'], content['sig'])

        if res == False:
            log_message(content)

        else:
            payload = content['payload']
            sender_pk = payload['sender_pk']
            receiver_pk = payload['receiver_pk']
            buy_currency = payload['buy_currency']
            sell_currency = payload['sell_currency']
            buy_amount = payload['buy_amount']
            sell_amount = payload['sell_amount']
            tx_id = payload['tx_id']
            signature = content['sig']
            new_order = {'sender_pk': sender_pk,
                          'receiver_pk': receiver_pk,
                          'buy_currency': buy_currency,
                          'sell_currency': sell_currency,
                          'buy_amount': buy_amount,
                          'sell_amount': sell_amount,
                          'tx_id': tx_id,
                          'signature': signature}
            txes = fill_order(new_order)
            execute_txes(txes)

        if res == True:
            return jsonify(True)
        else:
            return jsonify(False)

@app.route('/order_book')
def order_book():
    # fields = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature", "tx_id", "receiver_pk", "sender_pk" ]
    
    # # Same as before
    # pass
    res = {'data': []}
    for o in g.session.query(Order).all():
        res['data'].append({'sender_pk': o.sender_pk,
                                'receiver_pk': o.receiver_pk,
                                'buy_currency': o.buy_currency,
                                'sell_currency': o.sell_currency,
                                'buy_amount': o.buy_amount,
                                'sell_amount': o.sell_amount,
                                'signature': o.signature})
    return jsonify(res)

if __name__ == '__main__':
    app.run(port='5002')
