import unittest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
import main

class TestEmailNotifications(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            "users": [
                {
                    "email": "test@example.com",
                    "certifications": [
                        {"credentialId": "D56FD78AFC38824E"}
                    ]
                }
            ]
        }

    @patch('main.send_email')
    @patch('main.requests.get')
    @patch('yaml.safe_load')
    @patch('main.today')
    def test_renewal_email_on_weekday(self, mock_today, mock_yaml_load, mock_get, mock_send_email):
        # Arrange
        mock_today.return_value = datetime(2023, 7, 4)  # A Tuesday
        mock_yaml_load.return_value = self.mock_config
        mock_get.return_value.json.return_value = {
            "title": "Azure Administrator Associate",
            "expiresOn": (datetime(2023, 7, 4) + timedelta(days=59)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        
        main.is_weekend = Mock(return_value=False)  # Ensure today is not a weekend

        # Act
        main.main()

        # Assert
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        self.assertEqual(args[0], "test@example.com")
        self.assertEqual(args[1], "Azure Administrator Associate expires in 59 days")

    @patch('main.send_email')
    @patch('main.requests.get')
    @patch('yaml.safe_load')
    @patch('main.today')
    def test_renewal_email_on_monday(self, mock_today, mock_yaml_load, mock_get, mock_send_email):
        # Arrange
        mock_today.return_value = datetime(2023, 7, 3)  # A Monday
        mock_yaml_load.return_value = self.mock_config
        mock_get.return_value.json.return_value = {
            "title": "Azure Administrator Associate",
            "expiresOn": (datetime(2023, 7, 3) + timedelta(days=179)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        
        main.is_weekend = Mock(return_value=False)

        # Act
        main.main()

        # Assert
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        self.assertEqual(args[0], "test@example.com")
        self.assertEqual(args[1], "Azure Administrator Associate is eligible for renewal")

    @patch('main.send_email')
    @patch('main.requests.get')
    @patch('yaml.safe_load')
    @patch('main.today')
    def test_no_email_120_days_before_expiration(self, mock_today, mock_yaml_load, mock_get, mock_send_email):
        # Arrange
        mock_today.return_value = datetime(2023, 7, 4)  # A Tuesday
        mock_yaml_load.return_value = self.mock_config
        mock_get.return_value.json.return_value = {
            "title": "Azure Administrator Associate",
            "expiresOn": (datetime(2023, 7, 4) + timedelta(days=120)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }

        # Act
        main.main()

        # Assert
        mock_send_email.assert_not_called()

    @patch('main.send_email')
    @patch('main.requests.get')
    @patch('yaml.safe_load')
    @patch('main.today')
    def test_expiration_email_60_days_before_expiration(self, mock_today, mock_yaml_load, mock_get, mock_send_email):
        # Arrange
        mock_today.return_value = datetime(2023, 7, 4)  # A Tuesday
        mock_yaml_load.return_value = self.mock_config
        mock_get.return_value.json.return_value = {
            "title": "Azure Administrator Associate",
            "expiresOn": (datetime(2023, 7, 4) + timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }

        # Act
        main.main()

        # Assert
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        self.assertEqual(args[0], "test@example.com")
        self.assertEqual(args[1], "Azure Administrator Associate expires in 60 days")

if __name__ == '__main__':
    unittest.main()
