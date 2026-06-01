
from fastapi import APIRouter
from services.order_service import create_order
router = APIRouter()

@router.post('/orders')
def order(user_id:int,item:str):
    return create_order(user_id,item)
