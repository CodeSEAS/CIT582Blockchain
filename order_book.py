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
    new_inserted_order = Order(sender_pk = order['sender_pk'], receiver_pk = order['receiver_pk'], buy_currency = order['buy_currency'], sell_currency = order['sell_currency'], buy_amount = order['buy_amount'], sell_amount = order['sell_amount'])
    session.add(new_inserted_order)
    session.commit()

    existing_order = session.query(Order).filter(Order.filled == None,
                                                 Order.sell_currency == order.buy_currency, 
                                                 Order.buy_currency == order.sell_currency,
                                                ((Order.sell_amount / Order.buy_amount) >= (order.buy_amount / order.sell_amount)),
                                                Order.sell_amount != Order.buy_amount, 
                                                order.buy_amount != order.sell_amount)
    if existing_order is None:
        return
    else:
        new_inserted_order.filled = datetime.now()
        existing_order.filled = datetime.now()
        new_inserted_order.counterparty_id = existing_order.id
        existing_order.counterparty_id = new_inserted_order.id

        if new_inserted_order.buy_amount > existing_order.sell_amount:
            new_inserted_order_existing_order_difference = new_inserted_order.buy_amount - existing_order.sell_amount
            new_inserted_order_rate = new_inserted_order.buy_amount / new_inserted_order.sell_amount

            modified_order = Order(creator_id = new_inserted_order.id, 
                                   sender_pk = new_inserted_order.sender_pk, 
                                   receiver_pk = new_inserted_order.receiver_pk, 
                                   buy_currency = new_inserted_order.buy_currency,
                                    sell_currency = new_inserted_order.sell_currency, 
                                    buy_amount = new_inserted_order_existing_order_difference, 
                                    sell_amount = new_inserted_order_existing_order_difference / new_inserted_order_rate)
            session.add(modified_order)
            session.commit()
            # process_order(modified_order)

        elif new_inserted_order.buy_amount < existing_order.sell_amount:
            new_inserted_order_existing_order_difference = existing_order.sell_amount - new_inserted_order.buy_amount
            new_inserted_order_rate = existing_order.sell_amount / existing_order.buy_amount

            modified_order = Order(creator_id = existing_order.id, 
                                   sender_pk = existing_order.sender_pk, 
                                   receiver_pk = existing_order.receiver_pk, 
                                   buy_currency = existing_order.buy_currency,
                                    sell_currency = existing_order.sell_currency, 
                                    buy_amount = new_inserted_order_existing_order_difference / new_inserted_order_rate, 
                                    sell_amount = new_inserted_order_existing_order_difference)
            session.add(modified_order)
            session.commit()
            # process_order(modified_order)
        else:
            session.commit()

        