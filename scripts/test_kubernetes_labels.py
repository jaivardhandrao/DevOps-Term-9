import unittest

from kubernetes_labels import validate_label_values


class LabelValidationTests(unittest.TestCase):
    def test_original_frontend_label_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_label_values({"version": "DevOps session 12 frontend"})

    def test_kubernetes_value_boundaries(self):
        for valid in ["", "a", "session-12-frontend", "release_1.2", "x" * 63]:
            validate_label_values({"version": valid})
        for invalid in ["a b", "-v1", "v1-", "x" * 64, True]:
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                validate_label_values({"version": invalid})


if __name__ == "__main__":
    unittest.main()
