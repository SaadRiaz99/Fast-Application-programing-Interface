from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(20), default="customer")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    cart_items = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    stock = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    cart_items = relationship("Cart", back_populates="product")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    image_url = Column(String(500))


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum("pending", "confirmed", "processing", "shipped", "delivered", "cancelled"), default="pending")
    shipping_address = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    subject = Column(String(200))
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
