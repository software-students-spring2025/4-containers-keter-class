"""
docstring
"""
def test_register(client):
    """
    idk
    """
    response = client.post(
        "/register",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Please log in" in response.data or b"Login" in response.data

def test_register_duplicate(client):
    """
    idk
    """
    client.post(
        "/register", data={"email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/register",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )

    # Updated to exact string from flash()
    assert b"Email already registered." in response.data


def test_login_success(client):
    """
    idk
    """
    client.post(
        "/register", data={"email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )

    assert b"Welcome" in response.data


def test_login_fail(client):
    """
    idk
    """
    response = client.post(
        "/login",
        data={"email": "notfound@example.com", "password": "wrong"},
        follow_redirects=True,
    )

    assert b"Invalid credentials" in response.data


def test_logout(client):
    """
    idk
    """
    client.post(
        "/register", data={"email": "test@example.com", "password": "password123"}
    )
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    response = client.get("/logout", follow_redirects=True)

    assert b"Login" in response.data
