"""Tests for twister.py."""

import unittest
import twister as t

class TestTwister(unittest.TestCase):
    def test_get_face_direction(self):
        self.assertEqual(t.get_face_direction((0, 3, 1, 4, 2, 5), 0), (-1, 0, 0))
        self.assertEqual(t.get_face_direction((0, 3, 1, 4, 2, 5), 3), (1, 0, 0))
        self.assertEqual(t.get_face_direction((0, 3, 1, 4, 2, 5), 1), (0, -1, 0))
        self.assertEqual(t.get_face_direction((0, 3, 1, 4, 2, 5), 4), (0, 1, 0))
        self.assertEqual(t.get_face_direction((0, 3, 1, 4, 2, 5), 2), (0, 0, -1))
        self.assertEqual(t.get_face_direction((0, 3, 1, 4, 2, 5), 5), (0, 0, 1))

    def test_is_location_valid_and_free(self):
        t.LOCATIONS.clear()
        t.LOCATIONS.append((0, 0, 0))
        self.assertTrue(t.is_location_valid_and_free((1, 1, 1)))
        self.assertTrue(t.is_location_valid_and_free((2, 2, 2)))
        self.assertTrue(t.is_location_valid_and_free((0, 0, 1)))
        self.assertTrue(t.is_location_valid_and_free((0, 1, 0)))

        self.assertFalse(t.is_location_valid_and_free((3, 3, 3)))  # Out of bounds
        self.assertFalse(t.is_location_valid_and_free((0, 0, 0)))  # Already occupied
        self.assertFalse(t.is_location_valid_and_free((-1, 0, 0))) # Out of bounds
        self.assertFalse(t.is_location_valid_and_free((0, -1, 0))) # Out of bounds
        self.assertFalse(t.is_location_valid_and_free((0, 0, -1))) # Out of bounds

if __name__ == "__main__":
    unittest.main()
