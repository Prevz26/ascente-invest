import unittest
from unittest.mock import MagicMock, patch
from v1.auth.service import AuthService, AlreadyExistsError, ServerError
# from ....src.v1.auth.service import AuthService
class TestServiceCreate(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_model = MagicMock()
        self.service = AuthService(db=self.mock_db, model=self.mock_model)

    @patch("invest.src.v1.auth.service.auth_logger")
    @patch("invest.src.v1.auth.service.Service.clean_email")
    @patch("invest.src.v1.auth.service.Service.hash_password")
    def test_create_user(self, mock_hash_password, mock_clean_email, mock_auth_logger):
        # Table-driven test cases
        test_cases = [
            {
                "name": "Successful user creation",
                "input": {"email": "test@example.com", "password": "password123"},
                "clean_email": "test@example.com",
                "existing_user": None,
                "hashed_password": "hashed_password123",
                "expected_exception": None,
                "expected_result": {"unique_id": "123", "email": "test@example.com"},
            },
            {
                "name": "User already exists",
                "input": {"email": "existing@example.com", "password": "password123"},
                "clean_email": "existing@example.com",
                "existing_user": MagicMock(),
                "hashed_password": None,
                "expected_exception": AlreadyExistsError,
                "expected_result": None,
            },
            {
                "name": "Database commit failure",
                "input": {"email": "fail@example.com", "password": "password123"},
                "clean_email": "fail@example.com",
                "existing_user": None,
                "hashed_password": "hashed_password123",
                "db_commit_side_effect": Exception("DB error"),
                "expected_exception": ServerError,
                "expected_result": None,
            },
        ]

        for case in test_cases:
            with self.subTest(case["name"]):
                # Mock dependencies
                mock_clean_email.return_value = case["clean_email"]
                mock_hash_password.return_value = case["hashed_password"]
                self.mock_db.query.return_value.filter_by.return_value.first.return_value = case["existing_user"]

                if "db_commit_side_effect" in case:
                    self.mock_db.commit.side_effect = case["db_commit_side_effect"]
                else:
                    self.mock_db.commit.side_effect = None

                # Prepare user model mock
                mock_user = MagicMock()
                mock_user.to_dict.return_value = case["expected_result"]
                self.mock_model.return_value = mock_user

                if case["expected_exception"]:
                    with self.assertRaises(case["expected_exception"]):
                        self.service.create(**case["input"])
                else:
                    result = self.service.create(**case["input"])
                    self.assertEqual(result, case["expected_result"])

                # Reset mocks for next iteration
                self.mock_db.reset_mock()
                mock_clean_email.reset_mock()
                mock_hash_password.reset_mock()

if __name__ == "__main__":
    unittest.main()