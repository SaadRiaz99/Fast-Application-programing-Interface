from models import Category, Product, User, Quote, ContactMessage, Order, OrderItem, Cart
from passlib.hash import pbkdf2_sha256


class TestStaticPages:
    def test_home_get(self, client, db):
        response = client.get("/")
        assert response.status_code == 200
        assert "PrintPress" in response.text

    def test_services_get(self, client, db):
        response = client.get("/services")
        assert response.status_code == 200

    def test_products_get(self, client, db):
        response = client.get("/products")
        assert response.status_code == 200

    def test_product_detail_no_id(self, client, db):
        response = client.get("/product")
        assert response.status_code == 200

    def test_product_detail_with_id_not_found(self, client, db):
        response = client.get("/product/999")
        assert response.status_code == 200

    def test_product_detail_with_id_found(self, client, db):
        cat = Category(name="Test", slug="test")
        db.add(cat)
        db.commit()
        prod = Product(name="Test Product", slug="test-product", price=10.99, category_id=cat.id)
        db.add(prod)
        db.commit()
        response = client.get(f"/product/{prod.id}")
        assert response.status_code == 200

    def test_about_get(self, client, db):
        response = client.get("/about")
        assert response.status_code == 200

    def test_contact_get(self, client, db):
        response = client.get("/contact")
        assert response.status_code == 200

    def test_cart_get(self, client, db):
        response = client.get("/cart")
        assert response.status_code == 200

    def test_checkout_get(self, client, db):
        response = client.get("/checkout")
        assert response.status_code == 200

    def test_login_get(self, client, db):
        response = client.get("/login")
        assert response.status_code == 200

    def test_signup_get(self, client, db):
        response = client.get("/signup")
        assert response.status_code == 200

    def test_quote_get(self, client, db):
        response = client.get("/quote")
        assert response.status_code == 200

    def test_orders_get(self, client, db):
        response = client.get("/orders")
        assert response.status_code == 200

    def test_dashboard_get(self, client, db):
        user = User(name="Admin", email="admin@test.com", password_hash=pbkdf2_sha256.hash("p"), role="admin")
        db.add(user)
        db.commit()
        db.refresh(user)
        client.cookies.set("user_id", str(user.id))
        client.cookies.set("user_role", "admin")
        response = client.get("/dashboard")
        assert response.status_code == 200

    def test_search_get(self, client, db):
        response = client.get("/search?q=test")
        assert response.status_code == 200

    def test_profile_redirects_when_not_logged_in(self, client, db):
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 303

    def test_order_detail_not_found(self, client, db):
        response = client.get("/order/999")
        assert response.status_code == 200


class TestQuoteForm:
    def test_submit_quote_success(self, client, db):
        response = client.post("/quote", data={
            "name": "Test User",
            "email": "test@example.com",
            "description": "Need 500 business cards"
        })
        assert response.status_code == 200
        assert db.query(Quote).count() == 1

    def test_submit_quote_missing_fields(self, client, db):
        response = client.post("/quote", data={
            "name": "Test User"
        })
        assert response.status_code == 422


class TestContactForm:
    def test_submit_contact_success(self, client, db):
        response = client.post("/contact", data={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Inquiry",
            "message": "I need printing services"
        })
        assert response.status_code == 200
        assert db.query(ContactMessage).count() == 1

    def test_submit_contact_missing_fields(self, client, db):
        response = client.post("/contact", data={
            "name": "Test User"
        })
        assert response.status_code == 422


class TestSignupLogin:
    def test_signup_success(self, client, db):
        response = client.post("/signup", data={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepass123",
            "phone": "1234567890"
        })
        assert response.status_code == 200
        assert db.query(User).count() == 1
        user = db.query(User).first()
        assert pbkdf2_sha256.verify("securepass123", user.password_hash)

    def test_signup_duplicate_email(self, client, db):
        hashed = pbkdf2_sha256.hash("pass")
        db.add(User(name="Existing", email="dup@example.com", password_hash=hashed))
        db.commit()
        response = client.post("/signup", data={
            "name": "Dup", "email": "dup@example.com",
            "password": "pass", "phone": ""
        })
        assert response.status_code == 200

    def test_signup_missing_fields(self, client, db):
        response = client.post("/signup", data={"name": "New User"})
        assert response.status_code == 422

    def test_login_success(self, client, db):
        hashed = pbkdf2_sha256.hash("mypassword")
        db.add(User(name="Test User", email="test@example.com", password_hash=hashed))
        db.commit()
        response = client.post("/login", data={
            "email": "test@example.com", "password": "mypassword"
        }, follow_redirects=False)
        assert response.status_code == 303

    def test_login_wrong_password(self, client, db):
        hashed = pbkdf2_sha256.hash("correctpass")
        db.add(User(name="Test", email="t@t.com", password_hash=hashed))
        db.commit()
        response = client.post("/login", data={
            "email": "t@t.com", "password": "wrongpass"
        })
        assert response.status_code == 200
        assert "Invalid email or password" in response.text

    def test_login_nonexistent_user(self, client, db):
        response = client.post("/login", data={
            "email": "noone@example.com", "password": "pass"
        })
        assert response.status_code == 200

    def test_logout(self, client, db):
        response = client.post("/logout", follow_redirects=False)
        assert response.status_code == 303


class TestCheckoutForm:
    def test_checkout_success(self, client, db):
        cat = Category(name="Cards", slug="cards")
        db.add(cat)
        db.commit()
        p1 = Product(id=1, name="Premium Business Cards", slug="pbc", price=25.00, category_id=cat.id)
        p2 = Product(id=2, name="A5 Flyers", slug="af", price=40.00, category_id=cat.id)
        db.add(p1)
        db.add(p2)
        db.commit()

        # First add items to cart
        client.post("/cart", data={"product_id": 1, "quantity": 2})

        response = client.post("/checkout", data={
            "name": "Order Client",
            "email": "order@example.com",
            "phone": "999888777",
            "address": "123 Main St",
            "city": "Metropolis",
            "postal_code": "12345"
        })
        assert response.status_code == 200
        assert db.query(Order).count() == 1


class TestDashboardContext:
    def test_dashboard_counts(self, client, db):
        cat = Category(name="Cat", slug="cat")
        db.add(cat)
        db.commit()
        db.add(Product(name="P1", slug="p1", price=10, category_id=cat.id))
        db.add(Product(name="P2", slug="p2", price=20, category_id=cat.id))
        db.commit()
        admin = User(name="Admin", email="admin2@test.com", password_hash=pbkdf2_sha256.hash("p"), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        client.cookies.set("user_id", str(admin.id))
        client.cookies.set("user_role", "admin")
        response = client.get("/dashboard")
        assert response.status_code == 200

    def test_orders_context(self, client, db):
        response = client.get("/orders")
        assert response.status_code == 200


class TestCartForm:
    def test_add_to_cart(self, client, db):
        cat = Category(name="Cards", slug="cards")
        db.add(cat)
        db.commit()
        prod = Product(id=1, name="Business Cards", slug="bc", price=25.00, category_id=cat.id)
        db.add(prod)
        db.commit()

        response = client.post("/cart", data={"product_id": 1, "quantity": 2}, follow_redirects=False)
        assert response.status_code == 303
        assert db.query(Cart).count() == 1
        assert db.query(Cart).first().quantity == 2

    def test_remove_from_cart(self, client, db):
        cat = Category(name="Cards", slug="cards")
        db.add(cat)
        db.commit()
        prod = Product(id=1, name="Business Cards", slug="bc", price=25.00, category_id=cat.id)
        db.add(prod)
        db.commit()

        client.post("/cart", data={"product_id": 1, "quantity": 1}, follow_redirects=False)

        response = client.post("/cart/remove", data={"product_id": 1}, follow_redirects=False)
        assert response.status_code == 303
        assert db.query(Cart).count() == 0


class TestOrderDetail:
    def test_order_detail_with_items(self, client, db):
        cat = Category(name="Cat", slug="cat")
        db.add(cat)
        db.commit()
        prod = Product(name="P1", slug="p1", price=10, category_id=cat.id, stock=5)
        db.add(prod)
        db.commit()

        user = User(name="U", email="u@u.com", password_hash=pbkdf2_sha256.hash("p"))
        db.add(user)
        db.commit()
        db.refresh(user)

        order = Order(user_id=user.id, total=20, status="processing", shipping_address="Addr")
        db.add(order)
        db.commit()
        db.refresh(order)

        oi = OrderItem(order_id=order.id, product_id=prod.id, quantity=2, price=10)
        db.add(oi)
        db.commit()

        response = client.get(f"/order/{order.id}")
        assert response.status_code == 200
        assert "processing" in response.text

    def test_profile_with_login(self, client, db):
        hashed = pbkdf2_sha256.hash("pass")
        user = User(name="Profile User", email="profile@test.com", password_hash=hashed)
        db.add(user)
        db.commit()
        db.refresh(user)

        client.cookies.set("user_id", str(user.id))
        client.cookies.set("user_name", "Profile User")
        response = client.get("/profile")
        assert response.status_code == 200
        assert "Profile User" in response.text


class TestOrderStatusUpdate:
    def test_order_status_update_success(self, client, db):
        cat = Category(name="Cat", slug="cat")
        db.add(cat)
        db.commit()
        prod = Product(name="P1", slug="p1", price=10, category_id=cat.id)
        db.add(prod)
        db.commit()
        user = User(name="U", email="u@u.com", password_hash=pbkdf2_sha256.hash("p"))
        db.add(user)
        db.commit()
        db.refresh(user)
        order = Order(user_id=user.id, total=50, status="pending", shipping_address="Addr")
        db.add(order)
        db.commit()
        db.refresh(order)

        client.cookies.set("user_id", str(user.id))
        response = client.post(f"/order/{order.id}/status", data={"status": "confirmed"}, follow_redirects=False)
        assert response.status_code == 303
        db.refresh(order)
        assert order.status == "confirmed"

    def test_order_status_update_invalid(self, client, db):
        cat = Category(name="Cat", slug="cat")
        db.add(cat)
        db.commit()
        prod = Product(name="P1", slug="p1", price=10, category_id=cat.id)
        db.add(prod)
        db.commit()
        user = User(name="U", email="u@u.com", password_hash=pbkdf2_sha256.hash("p"))
        db.add(user)
        db.commit()
        db.refresh(user)
        order = Order(user_id=user.id, total=50, status="pending", shipping_address="Addr")
        db.add(order)
        db.commit()
        db.refresh(order)

        response = client.post(f"/order/{order.id}/status", data={"status": "invalid_status"}, follow_redirects=False)
        assert response.status_code == 303
        db.refresh(order)
        assert order.status == "pending"

    def test_order_status_update_not_found(self, client, db):
        client.cookies.set("user_id", "1")
        response = client.post("/order/999/status", data={"status": "confirmed"}, follow_redirects=False)
        assert response.status_code == 303

    def test_dashboard_orders_page(self, client, db):
        admin = User(name="Admin", email="admin3@test.com", password_hash=pbkdf2_sha256.hash("p"), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        client.cookies.set("user_id", str(admin.id))
        client.cookies.set("user_role", "admin")
        response = client.get("/dashboard/orders")
        assert response.status_code == 200

    def test_dashboard_with_pending_orders(self, client, db):
        cat = Category(name="Cat", slug="cat")
        db.add(cat)
        db.commit()
        prod = Product(name="P1", slug="p1", price=10, category_id=cat.id)
        db.add(prod)
        db.commit()
        user = User(name="U", email="u@u.com", password_hash=pbkdf2_sha256.hash("p"))
        db.add(user)
        db.commit()
        db.refresh(user)
        order = Order(user_id=user.id, total=50, status="pending", shipping_address="Addr")
        db.add(order)
        db.commit()
        admin = User(name="Admin", email="admin4@test.com", password_hash=pbkdf2_sha256.hash("p"), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)

        client.cookies.set("user_id", str(admin.id))
        client.cookies.set("user_role", "admin")
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "pending" in response.text

    def test_dashboard_orders_with_data(self, client, db):
        cat = Category(name="Cat", slug="cat")
        db.add(cat)
        db.commit()
        prod = Product(name="P1", slug="p1", price=10, category_id=cat.id)
        db.add(prod)
        db.commit()
        admin = User(name="Admin", email="admin5@test.com", password_hash=pbkdf2_sha256.hash("p"), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        order = Order(user_id=admin.id, total=50, status="pending", shipping_address="Addr")
        db.add(order)
        db.commit()

        client.cookies.set("user_id", str(admin.id))
        client.cookies.set("user_role", "admin")
        response = client.get("/dashboard/orders")
        assert response.status_code == 200
        assert "#PRT-" in response.text

    def test_dashboard_redirects_non_admin(self, client, db):
        user = User(name="Regular", email="reg@test.com", password_hash=pbkdf2_sha256.hash("p"), role="customer")
        db.add(user)
        db.commit()
        db.refresh(user)

        client.cookies.set("user_id", str(user.id))
        client.cookies.set("user_role", "customer")
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 303

    def test_dashboard_redirects_guest(self, client, db):
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 303
