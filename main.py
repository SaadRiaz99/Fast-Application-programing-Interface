from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User, Category, Product, Service, Cart, Order, ContactMessage, Quote

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="template")


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return templates.TemplateResponse(request, "landing.html", {"categories": categories})


@app.get("/services")
async def services(request: Request, db: Session = Depends(get_db)):
    all_services = db.query(Service).all()
    return templates.TemplateResponse(request, "services.html", {"services": all_services})


@app.get("/products")
async def products(request: Request, db: Session = Depends(get_db)):
    all_products = db.query(Product).all()
    return templates.TemplateResponse(request, "products.html", {"products": all_products})


@app.get("/product")
async def product(request: Request):
    return templates.TemplateResponse(request, "product.html")

@app.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    return templates.TemplateResponse(request, "product.html", {"product": product})


@app.get("/quote")
async def quote_page(request: Request):
    return templates.TemplateResponse(request, "quote.html")


@app.post("/quote")
async def submit_quote(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    quote = Quote(name=name, email=email, description=description)
    db.add(quote)
    db.commit()
    return templates.TemplateResponse(request, "quote.html", {"success": True})


@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse(request, "about.html")


@app.get("/contact")
async def contact_page(request: Request):
    return templates.TemplateResponse(request, "contact.html")


@app.post("/contact")
async def submit_contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(""),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    contact = ContactMessage(name=name, email=email, subject=subject, message=message)
    db.add(contact)
    db.commit()
    return templates.TemplateResponse(request, "contact.html", {"success": True})


@app.get("/cart")
async def cart(request: Request):
    return templates.TemplateResponse(request, "cart.html")


@app.get("/checkout")
async def checkout(request: Request):
    return templates.TemplateResponse(request, "checkout.html")


@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    total_orders = db.query(Order).count()
    total_products = db.query(Product).count()
    total_messages = db.query(ContactMessage).count()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"total_orders": total_orders, "total_products": total_products, "total_messages": total_messages},
    )


@app.get("/orders")
async def orders(request: Request, db: Session = Depends(get_db)):
    all_orders = db.query(Order).all()
    return templates.TemplateResponse(request, "orders.html", {"orders": all_orders})


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")


@app.post("/signup")
async def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: str = Form(""),
    db: Session = Depends(get_db),
):
    user = User(name=name, email=email, password_hash=password, phone=phone)
    db.add(user)
    db.commit()
    return templates.TemplateResponse(request, "login.html", {"signup_success": True})
