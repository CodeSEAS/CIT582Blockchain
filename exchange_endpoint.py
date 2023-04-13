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
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """

def check_sig(payload,sig):
    request_sig = sig
    payload_platform = payload['platform']
    payload_pk = payload['pk']
    payload_message = json.dumps(payload)

    if payload_platform == 'Ethereum':
        # The signature should be on the entire payload dictionary not just the single “message” field.
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

def fill_order(order,txes=[]):
    session = g.session
    new_inserted_order = Order(sender_pk = order['sender_pk'], 
                               receiver_pk = order['receiver_pk'], 
                               buy_currency = order['buy_currency'], 
                               sell_currency = order['sell_currency'], 
                               buy_amount = order['buy_amount'], 
                               sell_amount = order['sell_amount'])
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
  
def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    message = json.dumps(d)
    g.session.add(Log(message = message))
    g.session.commit()

""" End of helper methods """



@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session

        # TODO: Check the signature
        result = check_sig(content['payload'],content['sig'])

        if result == False:
            log_message(content)
            return jsonify(False)
        
        # TODO: Add the order to the database
        payload = content['payload']
        sender_pk = payload['sender_pk']
        receiver_pk = payload['receiver_pk']
        buy_currency = payload['buy_currency']
        sell_currency = payload['sell_currency']
        buy_amount = payload['buy_amount']
        sell_amount = payload['sell_amount']
        new_order = Order(sender_pk = sender_pk,
                        receiver_pk = receiver_pk, 
                        buy_currency = buy_currency,
                        sell_currency = sell_currency, 
                        buy_amount = buy_amount, 
                        sell_amount = sell_amount)
        print(f'trade: type({type(new_order)}), new_order: {new_order}')
        # TODO: Fill the order
        fill_order(new_order)
        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        if result == True:
            return jsonify(True)
        else:
            return jsonify(False)

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
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