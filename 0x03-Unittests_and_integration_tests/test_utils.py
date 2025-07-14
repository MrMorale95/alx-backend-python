#!/usr/bin/env python3
"""
This module contains unit tests for the function access_nested_map
defined in the utils module.
"""

import unittest
from typing import Any, Dict, Tuple
from parameterized import parameterized
from utils import access_nested_map

class TestAccessNestedMap(unittest.TestCase):
    """Unit test class to test access_nested_map function behavior."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self,
                               nested_map: Dict,
                               path: Tuple,
                               expected: Any) -> None:
        """Test access_nested_map returns correct value for given nested_map and path."""
        self.assertEqual(access_nested_map(nested_map, path), expected)
