"""
Testing for Flask Routes
"""


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


def test_save_card_api(client):
    """
    test save card api
    """
    test_data = {
        "cardholder_name": "John Doe",
        "card_number": "1234 5678 9012 3456",
        "cvv": "123",
        "expiry_date": "12/26",
        "username": "johndoe",
        "cardname": "TestCard2",
    }
    response = client.post("/api/save_card", json=test_data)
    assert response.status_code == 302  # Redirect to dashboard


def test_dashboard_with_session(client):
    """
    test dashboard with session
    """
    with client.session_transaction() as sess:
        sess["user"] = "testuser"
    response = client.get("/dashboard")
    assert response.status_code == 200
