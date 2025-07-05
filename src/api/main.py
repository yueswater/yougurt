from fastapi import FastAPI

from src.api.routes import member_routes

app = FastAPI(title="Yougurt API")

app.include_router(member_routes.router, prefix="api/members", tags=["members"])
