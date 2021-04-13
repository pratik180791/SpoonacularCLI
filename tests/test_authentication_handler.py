from SpoonacularCLI.utils.authentication_handler import AuthenticationHandler, KeyAuthenticator
from unittest.mock import patch
import pytest
import unittest


class TestAuthenticationHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.AuthenticationHandler = AuthenticationHandler(KeyAuthenticator("someurl", None,None))

    def test_api_key_with_url(self):
        self.assertEqual(self.AuthenticationHandler.api_key(), "NOT IMPLEMENTED")

    def test_api_key_no_url(self):
        auth = AuthenticationHandler()
        self.assertNotEqual(auth.api_key(), "NOT IMPLEMENTED")
