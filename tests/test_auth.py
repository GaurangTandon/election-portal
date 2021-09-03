import pytest

CAS_REDIRECT = (
    "https://login.iiit.ac.in/cas/login?service=http%3A%2F%2Flocalhost%3A5000%2Flogin"
)
LOGIN_REDIRECT = "http://localhost/login"


def has_redirected_to_target(response, redirect_url: str):
    """
    Checks if given response is valid redirection
    """
    assert response.status_code == 302
    assert redirect_url == response.headers["Location"]
    return True


def test_login(client, app):
    # redirects without ticket
    assert has_redirected_to_target(client.get("/login"), CAS_REDIRECT)
    # redirects with invalid ticket
    assert has_redirected_to_target(client.get("/login?ticket=abcd"), LOGIN_REDIRECT)
