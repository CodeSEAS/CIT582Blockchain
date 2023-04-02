from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def process_order(order):
    #Your code here
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
        if existing_order.buy_currency != new_inserted_order.sell_currency:
            continue
        if existing_order.sell_currency != new_inserted_order.buy_currency:
            continue
        if existing_order.sell_amount / existing_order.buy_amount < new_inserted_order.buy_amount/ new_inserted_order.sell_amount:
            continue
        new_inserted_order.filled = datetime.now()
        existing_order.filled = datetime.now()
        new_inserted_order.counterparty_id = existing_order.id
        existing_order.counterparty_id = new_inserted_order.id
        session.commit()

        if new_inserted_order.sell_amount > existing_order.buy_amount:
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
        elif new_inserted_order.sell_amount < existing_order.buy_amount:
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
        break
    return    

        