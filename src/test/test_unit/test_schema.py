import pytest 
#this will be used to test all the schemas

from v1.auth.schema import RegistrationSchema, LoginSchema
from pydantic import ValidationError
@pytest.mark.parametrize(
    "username, fullname, email, password, confirm_password, country",
    [
        ("testuser", "Test User", "test@email.com", "Pass123!", "Pass123!", "Kenya"),
        ("user2", "User Two", "user2@email.com", "Password123", "Password123", "Uganda")
    ]
)

def test_normal_registration_schema(username, fullname, email, password, confirm_password, country):
    data = {
        "username": username,
        "fullname": fullname,
        "email": email,
        "password": password,
        "confirm_password": confirm_password,
        "country": country
    }
    assert RegistrationSchema(**data).model_dump()



@pytest.mark.parametrize(
    "username, fullname, email, password, confirm_password, country",
    [
        ("", "Empty User", "empty@email.com", "Pass123!", "Pass123!", "Tanzania"),  # Empty username
        ("test.user", "Test User", "invalid-email", "Pass123!", "Pass123!", "Kenya"),  # Invalid email
        ("testuser", "Test User", "test@email.com", "pass", "pass", "Kenya"),  # Short password
        ("testuser", "Test User", "test@email.com", "Pass123!", "DifferentPass", "Kenya"),  # Non-matching passwords
    ]
)
def test_edge_registration_schema(username, fullname, email, password, confirm_password, country):
    data = {
        "username": username,
        "fullname": fullname,
        "email": email,
        "password": password,
        "confirm_password": confirm_password,
        "country": country
    }
    with pytest.raises(ValidationError):
        assert RegistrationSchema(**data).model_dump()



@pytest.mark.parametrize(
        "username, password",
        [
            ("testuser", "password123"),
            ("user2", "securepass"),
            ("regular_user", "Pass123!")
        ]
    )
def test_normal_login_schema(username, password):
        data = {
            "username": username,
            "password": password
        }
        assert LoginSchema(**data).model_dump()

@pytest.mark.parametrize(
        "username, password",
        [
            ("", "password123"),  # Empty username
            ("testuser", ""),     # Empty password
            (" ", "password123")  # Whitespace username
        ]
    )
def test_invalid_login_schema(username, password):
        data = {
            "username": username, 
            "password": password
        }
        with pytest.raises(ValidationError):
            LoginSchema(**data).model_dump()
