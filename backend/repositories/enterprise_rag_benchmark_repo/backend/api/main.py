
from fastapi import FastAPI
from routes.user_routes import router as user_router
from routes.order_routes import router as order_router

app = FastAPI()
app.include_router(user_router)
app.include_router(order_router)
