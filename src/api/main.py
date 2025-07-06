from fastapi import FastAPI

from src.api.routes import member_routes

# Create a FastAPI application instance
app = FastAPI(title="Yougurt API")

# Register the member API routes with a URL prefix and Swagger tag
app.include_router(member_routes.router, prefix="/api/members", tags=["members"])
