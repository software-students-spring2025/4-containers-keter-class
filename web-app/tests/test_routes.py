"""
Testing for Flask Routes
"""
from bson import ObjectId


def test_upload_route_no_session(client):
    """
    test for /upload route
    """
    response = client.get("/upload")
    assert response.status_code == 302
    assert "/login" in response.location


def test_home_without_session(client):
    """
    test for /
    """
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_dashboard_without_session(client):
    """
    test dashboard without session
    """
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_verify_info(client):
    """
    test for /verify_info route
    """
    response = client.get("/verify_info")
    assert response.status_code == 200


def test_verify_info_api(client):
    """
    test verify info api
    """
    test_data = {
        "cardholder_name": "John Doe",
        "card_number": "1234 5678 9012 3456",
        "cvv": "123",
        "expiry_date": "12/26",
        "username": "johndoe",
        "cardname": "TestCard2",
    }
    response = client.post("/verify_info", json=test_data)
    assert response.status_code == 302  # Redirect to dashboard


def test_dashboard_with_session(client):
    """
    test dashboard with session
    """
    with client.session_transaction() as sess:
        sess["user"] = "testuser"
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_retrieve_api(client):
    """
    test retrieve api
    """
    test_data = {
        "cardholder_name": "John Doe",
        "card_number": "1234 5678 9012 3456",
        "cvv": "123",
        "expiry_date": "12/26",
        "username": "johndoe",
        "cardname": "TestCard2",
    }
    response = client.post("/retrieve", json=test_data)
    assert response.status_code == 302  # Redirect to verify_info


def test_scan_error(client):
    """
    test scan error api
    """
    response = client.get(
        "/scan_error", query_string={"missing_fields": "card_number,cvv"}
    )
    assert response.status_code == 200  # Redirect to verify_info


def test_delete_card(client):
    """
    test delete card
    """
    dummy_card = {
        "username": "testuser",
        "cardname": "TestCardToDelete",
        "cardholder_name": "Test User",
        "card_number": "1111 2222 3333 4444",
        "cvv": "123",
        "expiry_date": "12/30",
    }
    inserted = client.application.db.cards.insert_one(dummy_card)
    card_id = str(inserted.inserted_id)

    # Simulate logged-in session
    with client.session_transaction() as sess:
        sess["user"] = "testuser"

    # Act: send POST request to delete the card
    response = client.post(f"/delete_card/{card_id}", follow_redirects=True)

    # Assert: check if the card was deleted from DB
    card = client.application.db.cards.find_one({"_id": ObjectId(card_id)})
    assert card is None  # Should be deleted
    assert response.status_code == 200
