from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.parser import CliESR, ShowRuntime

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Eltex CLI Observer",
            "mode": None
        },
    )


@app.get("/vpp-show-runtime", response_class=HTMLResponse)
async def vpp_show_runtime_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "VPP NGFW Observer",
            "mode": "vpp_show_runtime",
        },
    )


@app.post("/vpp-show-runtime/parse", response_class=HTMLResponse)
async def show_runtime(request: Request, raw_text: str = Form(...)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "VPP NGFW Observer",
            "mode": "vpp_show_runtime",
            "raw_text": raw_text,
            "parsed_show_runtime": ShowRuntime(raw_text).parsing(),
        },
    )


@app.get("/esr-cli", response_class=HTMLResponse)
async def esr_cli_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ESR CLI Observer",
            "mode": "cli_esr",
        },
    )


@app.post("/esr-cli/parse", response_class=HTMLResponse)
async def cli_esr(request: Request, raw_text: str = Form(...)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ESR CLI Observer",
            "mode": "cli_esr",
            "raw_text": raw_text,
            "parsed_cli_esr": CliESR(raw_text).parsing(),
        },
    )
