
from repositories.order_repository import save_order
from integrations.payment_gateway import charge_customer

def create_order(user_id,item):
    charge_customer(user_id,100)
    return save_order(user_id,item)
