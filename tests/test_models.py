import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Category, Product, Service, Cart, Order, OrderItem, ContactMessage, Quote


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


class TestUserModel:
    def test_create_user(self, session):
        user = User(name="John Doe", email="john@example.com", password_hash="hashed123", phone="1234567890")
        session.add(user)
        session.commit()
        assert user.id is not None
        assert user.name == "John Doe"

    def test_user_str(self, session):
        user = User(name="Jane", email="jane@example.com", password_hash="hash")
        session.add(user)
        session.commit()
        assert user.email == "jane@example.com"


class TestCategoryModel:
    def test_create_category(self, session):
        cat = Category(name="Business Cards", slug="business-cards")
        session.add(cat)
        session.commit()
        assert cat.id is not None
        assert cat.slug == "business-cards"


class TestProductModel:
    def test_create_product(self, session):
        cat = Category(name="Cat", slug="cat")
        session.add(cat)
        session.commit()
        prod = Product(name="Premium Cards", slug="premium-cards", description="High quality", price=25.00, category_id=cat.id, stock=100)
        session.add(prod)
        session.commit()
        assert prod.id is not None
        assert prod.price == 25.00

    def test_product_category_relation(self, session):
        cat = Category(name="Flyers", slug="flyers")
        session.add(cat)
        session.commit()
        prod = Product(name="A5 Flyer", slug="a5-flyer", price=40.00, category_id=cat.id)
        session.add(prod)
        session.commit()
        assert prod.category.name == "Flyers"
        assert cat.products[0].name == "A5 Flyer"


class TestServiceModel:
    def test_create_service(self, session):
        svc = Service(name="Digital Printing", description="Fast turnaround", price=50.00)
        session.add(svc)
        session.commit()
        assert svc.id is not None
        assert svc.name == "Digital Printing"


class TestCartModel:
    def test_create_cart_item(self, session):
        user = User(name="U", email="u@e.com", password_hash="h")
        session.add(user)
        session.commit()
        cat = Category(name="C", slug="c")
        session.add(cat)
        session.commit()
        prod = Product(name="P", slug="p", price=10, category_id=cat.id)
        session.add(prod)
        session.commit()
        cart = Cart(user_id=user.id, product_id=prod.id, quantity=2)
        session.add(cart)
        session.commit()
        assert cart.id is not None
        assert cart.quantity == 2


class TestOrderModel:
    def test_create_order(self, session):
        user = User(name="U", email="u@e.com", password_hash="h")
        session.add(user)
        session.commit()
        order = Order(user_id=user.id, total=100.00, shipping_address="123 Street")
        session.add(order)
        session.commit()
        assert order.id is not None
        assert order.status == "pending"

    def test_order_items_relation(self, session):
        user = User(name="U", email="u@e.com", password_hash="h")
        session.add(user)
        session.commit()
        cat = Category(name="C", slug="c")
        session.add(cat)
        session.commit()
        prod = Product(name="P", slug="p", price=10, category_id=cat.id)
        session.add(prod)
        session.commit()
        order = Order(user_id=user.id, total=20.00)
        session.add(order)
        session.commit()
        item = OrderItem(order_id=order.id, product_id=prod.id, quantity=2, price=10.00)
        session.add(item)
        session.commit()
        assert len(order.items) == 1
        assert order.items[0].product_id == prod.id


class TestContactMessageModel:
    def test_create_contact_message(self, session):
        msg = ContactMessage(name="Test", email="t@t.com", subject="Hello", message="Test message")
        session.add(msg)
        session.commit()
        assert msg.id is not None


class TestQuoteModel:
    def test_create_quote(self, session):
        q = Quote(name="Test", email="t@t.com", description="Need printing")
        session.add(q)
        session.commit()
        assert q.id is not None
