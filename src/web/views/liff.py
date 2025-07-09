from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/liff/bind", response_class=HTMLResponse)
async def liff_bind_page(request: Request):
    return templates.TemplateResponse("liff/bind.html", {"request": request})
