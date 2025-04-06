import pytest
from unittest.mock import Mock, patch
from v1.auth.service import AuthService
from utils.exceptions import AlreadyExistsError

def test_create_user_success(mocker):
    # Mock dependencies
    mock_db = mocker.Mock()
    mock_model = mocker.Mock()
    
    # Setup test data
    test_data = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }

    # Configure mocks
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    mock_model.return_value.to_dict.return_value = test_data
    
    # Create service instance with mocked dependencies 
    service = AuthService(model=mock_model)
    service.db = mock_db
    
    # Mock hash_password method
    service.hash_password = mocker.Mock(return_value="hashed_password")

    # Execute
    result = service.create(**test_data)

    # Assert
    assert result == test_data
    mock_db.query.assert_called_once()
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_user_already_exists(mocker):
    # Mock dependencies
    mock_db = mocker.Mock()
    mock_model = mocker.Mock()
    
    # Setup test data
    test_data = {
        "email": "test@example.com", 
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }

    # Configure mocks to simulate existing user
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_model
    
    # Create service instance
    service = AuthService(model=mock_model)
    service.db = mock_db

    # Assert raises error
    with pytest.raises(AlreadyExistsError):
        service.create(**test_data)