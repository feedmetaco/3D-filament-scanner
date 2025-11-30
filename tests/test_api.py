import os
import sys
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Ensure the app uses an in-memory database for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from backend.database import engine, get_session  # noqa: E402
from backend.main import app  # noqa: E402


def override_get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
def setup_database() -> Iterator[None]:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_create_and_retrieve_product(client: TestClient) -> None:
    payload = {
        "brand": "Sunlu",
        "line": "PLA+",
        "material": "PLA",
        "color_name": "Yellow",
        "diameter_mm": 1.75,
        "notes": "Test product",
        "barcode": "1234567890",
        "sku": "SUN-PLA-YEL",
    }

    response = client.post("/api/v1/products", json=payload)
    assert response.status_code == 200
    product = response.json()

    fetched = client.get(f"/api/v1/products/{product['id']}")
    assert fetched.status_code == 200
    retrieved = fetched.json()

    assert retrieved["brand"] == payload["brand"]
    assert retrieved["diameter_mm"] == payload["diameter_mm"]


def test_create_and_update_spool(client: TestClient) -> None:
    product_payload = {
        "brand": "Bambu",
        "line": "PLA Basic",
        "material": "PLA",
        "color_name": "White",
        "diameter_mm": 1.75,
    }
    product_resp = client.post("/api/v1/products", json=product_payload)
    assert product_resp.status_code == 200
    product_id = product_resp.json()["id"]

    spool_payload = {
        "product_id": product_id,
        "vendor": "Bambu",
        "price": 25.5,
        "storage_location": "Shelf A2",
        "status": "in_stock",
    }

    spool_resp = client.post("/api/v1/spools", json=spool_payload)
    assert spool_resp.status_code == 200
    spool = spool_resp.json()

    update_payload = {"status": "used_up"}
    update_resp = client.put(
        f"/api/v1/spools/{spool['id']}",
        json=update_payload,
    )
    assert update_resp.status_code == 200

    fetched_resp = client.get(f"/api/v1/spools/{spool['id']}")
    assert fetched_resp.status_code == 200
    assert fetched_resp.json()["status"] == "used_up"


def test_filter_products_by_brand(client: TestClient) -> None:
    # Create multiple products with different brands
    products = [
        {
            "brand": "Sunlu",
            "material": "PLA",
            "color_name": "Red",
            "diameter_mm": 1.75,
        },
        {
            "brand": "eSUN",
            "material": "PLA",
            "color_name": "Blue",
            "diameter_mm": 1.75,
        },
        {
            "brand": "Sunlu",
            "material": "PETG",
            "color_name": "Green",
            "diameter_mm": 1.75,
        },
    ]

    for product in products:
        response = client.post("/api/v1/products", json=product)
        assert response.status_code == 200

    # Filter by brand
    response = client.get("/api/v1/products?brand=Sunlu")
    assert response.status_code == 200
    filtered_products = response.json()
    assert len(filtered_products) == 2
    assert all(p["brand"] == "Sunlu" for p in filtered_products)


def test_filter_products_by_material_and_color(client: TestClient) -> None:
    # Create multiple products
    products = [
        {
            "brand": "Bambu",
            "material": "PLA",
            "color_name": "White",
            "diameter_mm": 1.75,
        },
        {
            "brand": "Bambu",
            "material": "PLA",
            "color_name": "Black",
            "diameter_mm": 1.75,
        },
        {
            "brand": "Sunlu",
            "material": "PETG",
            "color_name": "White",
            "diameter_mm": 1.75,
        },
    ]

    for product in products:
        response = client.post("/api/v1/products", json=product)
        assert response.status_code == 200

    # Filter by material and color
    response = client.get("/api/v1/products?material=PLA&color_name=White")
    assert response.status_code == 200
    filtered_products = response.json()
    assert len(filtered_products) == 1
    assert filtered_products[0]["material"] == "PLA"
    assert filtered_products[0]["color_name"] == "White"


def test_filter_spools_by_status(client: TestClient) -> None:
    # Create a product first
    product_payload = {
        "brand": "Sunlu",
        "material": "PLA",
        "color_name": "Yellow",
        "diameter_mm": 1.75,
    }
    product_resp = client.post("/api/v1/products", json=product_payload)
    product_id = product_resp.json()["id"]

    # Create multiple spools with different statuses
    spools = [
        {"product_id": product_id, "status": "in_stock"},
        {"product_id": product_id, "status": "used_up"},
        {"product_id": product_id, "status": "in_stock"},
    ]

    for spool in spools:
        response = client.post("/api/v1/spools", json=spool)
        assert response.status_code == 200

    # Filter by status
    response = client.get("/api/v1/spools?status=in_stock")
    assert response.status_code == 200
    filtered_spools = response.json()
    assert len(filtered_spools) == 2
    assert all(s["status"] == "in_stock" for s in filtered_spools)


def test_filter_spools_by_product_id(client: TestClient) -> None:
    # Create two products
    product1 = client.post(
        "/api/v1/products",
        json={
            "brand": "Sunlu",
            "material": "PLA",
            "color_name": "Red",
            "diameter_mm": 1.75,
        },
    ).json()
    product2 = client.post(
        "/api/v1/products",
        json={
            "brand": "eSUN",
            "material": "PETG",
            "color_name": "Blue",
            "diameter_mm": 1.75,
        },
    ).json()

    # Create spools for both products
    client.post("/api/v1/spools", json={"product_id": product1["id"]})
    client.post("/api/v1/spools", json={"product_id": product1["id"]})
    client.post("/api/v1/spools", json={"product_id": product2["id"]})

    # Filter by product_id
    response = client.get(f"/api/v1/spools?product_id={product1['id']}")
    assert response.status_code == 200
    filtered_spools = response.json()
    assert len(filtered_spools) == 2
    assert all(s["product_id"] == product1["id"] for s in filtered_spools)


def test_mark_spool_used(client: TestClient) -> None:
    # Create a product
    product_payload = {
        "brand": "Bambu",
        "material": "PLA",
        "color_name": "White",
        "diameter_mm": 1.75,
    }
    product_resp = client.post("/api/v1/products", json=product_payload)
    product_id = product_resp.json()["id"]

    # Create a spool
    spool_payload = {
        "product_id": product_id,
        "vendor": "Bambu",
        "status": "in_stock",
    }
    spool_resp = client.post("/api/v1/spools", json=spool_payload)
    spool_id = spool_resp.json()["id"]

    # Mark spool as used
    mark_used_resp = client.post(f"/api/v1/spools/{spool_id}/mark-used")
    assert mark_used_resp.status_code == 200
    updated_spool = mark_used_resp.json()
    assert updated_spool["status"] == "used_up"

    # Verify the status persisted
    fetched_resp = client.get(f"/api/v1/spools/{spool_id}")
    assert fetched_resp.status_code == 200
    assert fetched_resp.json()["status"] == "used_up"


def test_mark_nonexistent_spool_used(client: TestClient) -> None:
    # Try to mark a non-existent spool as used
    response = client.post("/api/v1/spools/99999/mark-used")
    assert response.status_code == 404
    assert response.json()["detail"] == "Spool not found"
