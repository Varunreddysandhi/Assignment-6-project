# Unit and property-style tests for both selection algorithms.

import random
import unittest

from selection import deterministic_select, randomized_select


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.methods = (
            deterministic_select,
            lambda data, k: randomized_select(data, k, rng=random.Random(2026)),
        )

    def test_fixed_examples_and_duplicates(self) -> None:
        cases = [
            [5],
            [3, 1, 2],
            [5, 5, 5, 5],
            [1, 1, 2, 2, 3, 3],
            [9, 2, 7, 2, 4, 8, 1],
            list(range(50)),
            list(range(49, -1, -1)),
            [-3, 0, -9, -3, 8, 0],
        ]
        for values in cases:
            original = values.copy()
            for k, expected in enumerate(sorted(values), 1):
                for method in self.methods:
                    with self.subTest(values=values[:5], k=k, method=method):
                        self.assertEqual(method(values, k), expected)
                        self.assertEqual(values, original)

    def test_random_property(self) -> None:
        rng = random.Random(123)
        for n in (1, 2, 5, 7, 25, 100, 503):
            for _ in range(18):
                values = [rng.randrange(-10, 11) for _ in range(n)]
                expected = sorted(values)
                for k in {1, (n + 1) // 2, n, rng.randrange(1, n + 1)}:
                    for method in self.methods:
                        self.assertEqual(method(values, k), expected[k - 1])

    def test_invalid_k(self) -> None:
        for method in self.methods:
            for values, k in (([], 1), ([5], 0), ([1, 2], 3)):
                with self.subTest(values=values, k=k):
                    with self.assertRaises(ValueError):
                        method(values, k)
            for k in (1.5, '2', True):
                with self.assertRaises(TypeError):
                    method([1, 2, 3], k)

    def test_comparable_non_integer_data(self) -> None:
        for method in self.methods:
            self.assertEqual(method(['pear', 'apple', 'plum', 'apple'], 2), 'apple')


if __name__ == '__main__':
    unittest.main()
