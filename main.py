from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.parser import ShowRuntime

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "VPP Observer",
        },
    )


@app.post("/parse", response_class=HTMLResponse)
async def show_runtime(request: Request, raw_text: str = Form(...)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "VPP Observer",
            "raw_text": raw_text,
            "parsed_show_runtime": ShowRuntime(raw_text).parsing(),
        },
    )
