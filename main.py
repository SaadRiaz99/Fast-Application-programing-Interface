from fastapi import FastAPI, Request, Depends, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, Category, Product, Service, Cart, Order, OrderItem, ContactMessage, Quote
from passlib.hash import pbkdf2_sha256

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="template")
templates.env.globals["PKR"] = "Rs"

def pkr(amount):
    return f"Rs {amount:,.2f}"

templates.env.globals["pkr"] = pkr


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


@app.get("/search")
async def search_products(request: Request, q: str = Query(""), db: Session = Depends(get_db)):
    if q:
        results = db.query(Product).filter(
            or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
        ).all()
    else:
        results = []
    return templates.TemplateResponse(request, "products.html", {"products": results, "search_query": q})


@app.get("/profile")
async def profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    user = db.query(User).filter(User.id == user_id).first() if user_id else None
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse(request, "profile.html", {"user": user, "orders": orders})


@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    return response


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


def _get_user_id(request: Request, db: Session) -> int:
    uid = request.cookies.get("user_id")
    if uid:
        user = db.query(User).filter(User.id == int(uid)).first()
        if user:
            return user.id
    guest = db.query(User).filter(User.email == "guest@printpress.com").first()
    if not guest:
        guest = User(name="Guest", email="guest@printpress.com", password_hash=pbkdf2_sha256.hash("guest"), phone="")
        db.add(guest)
        db.commit()
        db.refresh(guest)
    return guest.id


def _get_current_user(request: Request, db: Session):
    uid = request.cookies.get("user_id")
    if uid:
        return db.query(User).filter(User.id == int(uid)).first()
    return None





@app.get("/cart")
async def cart(request: Request, db: Session = Depends(get_db)):
    user_id = _get_user_id(request, db)
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    subtotal = float(sum(item.product.price * item.quantity for item in cart_items)) if cart_items else 0
    return templates.TemplateResponse(
        request,
        "cart.html",
        {"cart_items": cart_items, "subtotal": subtotal, "total": subtotal}
    )


@app.post("/cart")
async def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db),
):
    user_id = _get_user_id(request, db)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    cart_item = db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(cart_item)

    db.commit()
    return RedirectResponse(url="/cart", status_code=303)


@app.post("/cart/remove")
async def remove_from_cart(
    request: Request,
    product_id: int = Form(...),
    db: Session = Depends(get_db),
):
    user_id = _get_user_id(request, db)
    cart_item = db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == product_id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
    return RedirectResponse(url="/cart", status_code=303)


@app.get("/checkout")
async def checkout(request: Request, db: Session = Depends(get_db)):
    user_id = _get_user_id(request, db)
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    subtotal = float(sum(item.product.price * item.quantity for item in cart_items)) if cart_items else 0
    return templates.TemplateResponse(
        request,
        "checkout.html",
        {"cart_items": cart_items, "total": subtotal}
    )


@app.post("/checkout")
async def process_checkout(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    address: str = Form(...),
    city: str = Form(...),
    postal_code: str = Form(...),
    db: Session = Depends(get_db),
):
    # Find or create User based on email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        hashed = pbkdf2_sha256.hash("checkout_user")
        user = User(name=name, email=email, password_hash=hashed, phone=phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Get cart items
    user_id = _get_user_id(request, db)
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    if not cart_items:
        return RedirectResponse(url="/cart", status_code=303)

    subtotal = float(sum(item.product.price * item.quantity for item in cart_items))

    # Create the Order
    full_address = f"{address}, {city}, {postal_code}"
    order = Order(
        user_id=user.id,
        total=subtotal,
        status="pending",
        shipping_address=full_address
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create OrderItems and clear cart
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.add(order_item)
        db.delete(item)

    db.commit()

    # Set cookies for the user
    response = templates.TemplateResponse(request, "checkout.html", {"success": True, "order_id": order.id, "total": 0.0})
    response.set_cookie(key="user_id", value=str(user.id), max_age=86400 * 7)
    response.set_cookie(key="user_name", value=user.name, max_age=86400 * 7)
    return response


@app.get("/order/{order_id}")
async def order_detail(request: Request, order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return templates.TemplateResponse(request, "orders.html", {"error": "Order not found"})
    admin = _check_admin(request, db) is not None
    return templates.TemplateResponse(request, "order_detail.html", {"order": order, "admin": admin})


@app.post("/order/{order_id}/status")
async def update_order_status(
    request: Request,
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    valid_statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        return RedirectResponse(url=f"/order/{order_id}", status_code=303)
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
    return RedirectResponse(url=f"/order/{order_id}", status_code=303)


def _check_admin(request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request, db)
    if not user or user.role != "admin":
        return None
    return user


@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    admin = _check_admin(request, db)
    if not admin:
        return RedirectResponse(url="/login", status_code=303)
    total_orders = db.query(Order).count()
    total_products = db.query(Product).count()
    total_messages = db.query(ContactMessage).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "total_orders": total_orders,
            "total_products": total_products,
            "total_messages": total_messages,
            "pending_orders": pending_orders,
            "recent_orders": recent_orders,
        },
    )


@app.get("/dashboard/orders")
async def dashboard_orders(request: Request, db: Session = Depends(get_db)):
    admin = _check_admin(request, db)
    if not admin:
        return RedirectResponse(url="/login", status_code=303)
    all_orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse(request, "dashboard_orders.html", {"orders": all_orders})


@app.get("/orders")
async def orders(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if user_id:
        all_orders = db.query(Order).filter(Order.user_id == int(user_id)).order_by(Order.created_at.desc()).all()
    else:
        all_orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse(request, "orders.html", {"orders": all_orders})


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
async def process_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if user and pbkdf2_sha256.verify(password, user.password_hash):
        redirect_url = "/dashboard" if user.role == "admin" else "/"
        response = RedirectResponse(url=redirect_url, status_code=303)
        response.set_cookie(key="user_id", value=str(user.id), max_age=86400 * 7)
        response.set_cookie(key="user_name", value=user.name, max_age=86400 * 7)
        response.set_cookie(key="user_role", value=user.role, max_age=86400 * 7)
        return response
    return templates.TemplateResponse(request, "login.html", {"error": "Invalid email or password"})


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
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(request, "signup.html", {"error": "Email already registered"})
    hashed = pbkdf2_sha256.hash(password)
    role = "admin" if email == "admin@printpress.com" else "customer"
    user = User(name=name, email=email, password_hash=hashed, phone=phone, role=role)
    db.add(user)
    db.commit()
    response = RedirectResponse(url="/login", status_code=303)
    response.set_cookie(key="user_role", value=role, max_age=86400 * 7)
    return templates.TemplateResponse(request, "login.html", {"signup_success": True})


@app.get("/dashboard/customers")
async def dashboard_customers(request: Request, db: Session = Depends(get_db)):
    admin = _check_admin(request, db)
    if not admin:
        return RedirectResponse(url="/login", status_code=303)
    users = db.query(User).all()
    return templates.TemplateResponse(request, "dashboard_customers.html", {"users": users})


@app.get("/dashboard/quotes")
async def dashboard_quotes(request: Request, db: Session = Depends(get_db)):
    admin = _check_admin(request, db)
    if not admin:
        return RedirectResponse(url="/login", status_code=303)
    quotes = db.query(Quote).all()
    return templates.TemplateResponse(request, "dashboard_quotes.html", {"quotes": quotes})


@app.get("/dashboard/messages")
async def dashboard_messages(request: Request, db: Session = Depends(get_db)):
    admin = _check_admin(request, db)
    if not admin:
        return RedirectResponse(url="/login", status_code=303)
    messages = db.query(ContactMessage).all()
    return templates.TemplateResponse(request, "dashboard_messages.html", {"messages": messages})
