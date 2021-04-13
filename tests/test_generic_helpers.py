from SpoonacularCLI.helpers import generic_helpers
from unittest.mock import patch
import pytest
import unittest


class TestGenericHelpers(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    @patch('builtins.input', return_value="Sample Input")
    def test_validate_input(self, mocked_input):
        output = generic_helpers.validate_input(input_message="Enter input of your choice",
                                                invalid_message="Invalid input, please try again")
        self.assertEqual(output, "Sample Input")

    @patch('builtins.input', side_effect=["ABC", "", "yes"])
    def test_validate_inputs_mixed_inputs(self, mock_value):
        input_message = "Enter input of your choice"
        invalid_message = "Invalid input, please try again"
        acceptable_values = ["yes", "no", "exit"]
        validate_output = generic_helpers.validate_input(input_message=input_message,
                                                         invalid_message=invalid_message,
                                                         acceptable_values=acceptable_values
                                                         )
        out, err = self.capsys.readouterr()
        assert "Invalid input, please try again" in out
        self.assertEqual(validate_output, "yes")
