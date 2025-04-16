import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
from core.seed_data import seed_data
from models import (
    blacklist_token_model, state_model, city_model, address_model, roles_model, user_model, game_model, discount_model,
    admin_revenue_model, turf_model, media_model, manage_turf_manager_model, turf_booking,
    revenue_model, feedback_model)
from core.constant import MESSAGE, WELCOME_MSG
from routers import users, admin, turf_owner, token, customer, turf_manager
from fastapi.staticfiles import StaticFiles

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

models = [
    blacklist_token_model, state_model, city_model, address_model, roles_model, user_model, game_model, discount_model,
    admin_revenue_model, turf_model, media_model, manage_turf_manager_model, turf_booking,
    revenue_model, feedback_model
]

# Create all tables using a loop
for model in models:
    model.Base.metadata.create_all(engine)

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(turf_owner.router)
app.include_router(customer.router)
app.include_router(turf_manager.router)

app.include_router(token.router)

app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get("/")
async def root():
    return {MESSAGE: WELCOME_MSG}


if __name__ == "__main__":
    seed_data()
    uvicorn.run(app, host="127.0.0.1", port=8001)