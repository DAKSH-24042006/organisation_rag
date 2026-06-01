
from repositories.user_repository import save_user,find_user
from events.notification_service import send_welcome_email

def validate_user(name):
    return len(name)>2

def create_user(name):
    if not validate_user(name):
        raise ValueError()
    user=save_user(name)
    send_welcome_email(user)
    return user

def get_user(user_id):
    return find_user(user_id)
