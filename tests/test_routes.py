from models import Category, Service, Product, User, Quote, ContactMessage, Order


class TestStaticPages:
    def test_home_get(self, client, db):
        response = client.get("/")
        assert response.status_code == 200
        assert "PrintPress" in response.text

    def test_services_get(self, client, db):
        response = client.get("/services")
        assert response.status_code == 200
        assert "PrintPress" in response.text

    def test_products_get(self, client, db):
        response = client.get("/products")
        assert response.status_code == 200
        assert "PrintPress" in response.text

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
        response = client.get("/dashboard")
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


class TestSignupForm:
    def test_signup_success(self, client, db):
        response = client.post("/signup", data={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepass123",
            "phone": "1234567890"
        })
        assert response.status_code == 200
        assert db.query(User).count() == 1

    def test_signup_missing_fields(self, client, db):
        response = client.post("/signup", data={
            "name": "New User"
        })
        assert response.status_code == 422


class TestDashboardContext:
    def test_dashboard_counts(self, client, db):
        cat = Category(name="Cat", slug="cat")
        db.add(cat)
        db.commit()
        db.add(Product(name="P1", slug="p1", price=10, category_id=cat.id))
        db.add(Product(name="P2", slug="p2", price=20, category_id=cat.id))
        db.commit()
        response = client.get("/dashboard")
        assert response.status_code == 200

    def test_orders_context(self, client, db):
        response = client.get("/orders")
        assert response.status_code == 200
