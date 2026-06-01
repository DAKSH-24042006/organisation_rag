
from fastapi import APIRouter
from services.user_service import create_user,get_user
router = APIRouter()

@router.post('/users')
def create(name:str):
    return create_user(name)

@router.get('/users/{user_id}')
def read(user_id:int):
    return get_user(user_id)
