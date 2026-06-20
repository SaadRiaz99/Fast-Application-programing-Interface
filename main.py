from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="template")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "landing.html")

@app.get("/services")
async def services(request: Request):
    return templates.TemplateResponse(request, "services.html")

@app.get("/products")
async def products(request: Request):
    return templates.TemplateResponse(request, "products.html")

@app.get("/product")
async def product(request: Request):
    return templates.TemplateResponse(request, "product.html")

@app.get("/quote")
async def quote(request: Request):
    return templates.TemplateResponse(request, "quote.html")

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse(request, "about.html")

@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html")

@app.get("/cart")
async def cart(request: Request):
    return templates.TemplateResponse(request, "cart.html")

@app.get("/checkout")
async def checkout(request: Request):
    return templates.TemplateResponse(request, "checkout.html")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/orders")
async def orders(request: Request):
    return templates.TemplateResponse(request, "orders.html")

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse(request, "signup.html")
