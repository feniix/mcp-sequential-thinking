import unittest

from mcp_sequential_thinking.utils import convert_dict_keys, to_camel_case, to_snake_case


class TestStringCaseUtils(unittest.TestCase):
    """Test cases for string case conversion utilities."""

    def test_to_camel_case(self):
        """Snake case keys are converted to camel case for API output."""
        self.assertEqual(to_camel_case("thought_number"), "thoughtNumber")
        self.assertEqual(to_camel_case("next_thought_needed"), "nextThoughtNeeded")
        self.assertEqual(to_camel_case("thought"), "thought")

    def test_to_snake_case(self):
        """Camel case keys are converted to snake case for internal models."""
        self.assertEqual(to_snake_case("thoughtNumber"), "thought_number")
        self.assertEqual(to_snake_case("nextThoughtNeeded"), "next_thought_needed")
        self.assertEqual(to_snake_case("HTTPServer"), "http_server")


class TestConvertDictKeys(unittest.TestCase):
    """Test cases for recursive dictionary key conversion."""

    def test_convert_dict_keys_recursively(self):
        """Nested dictionaries inside dictionaries and lists are converted."""
        data = {
            "thought_number": 1,
            "metadata": {
                "next_thought_needed": True,
                "nested_items": [
                    {"axioms_used": ["clarity"]},
                    "unchanged scalar",
                ],
            },
        }

        result = convert_dict_keys(data, to_camel_case)

        self.assertEqual(
            result,
            {
                "thoughtNumber": 1,
                "metadata": {
                    "nextThoughtNeeded": True,
                    "nestedItems": [
                        {"axiomsUsed": ["clarity"]},
                        "unchanged scalar",
                    ],
                },
            },
        )

    def test_convert_dict_keys_returns_non_dict_values_unchanged(self):
        """Non-dictionary inputs are returned unchanged."""
        self.assertEqual(
            convert_dict_keys(["not", "a", "dict"], to_camel_case), ["not", "a", "dict"]
        )
        self.assertEqual(convert_dict_keys("thought_number", to_camel_case), "thought_number")


if __name__ == "__main__":
    unittest.main()
