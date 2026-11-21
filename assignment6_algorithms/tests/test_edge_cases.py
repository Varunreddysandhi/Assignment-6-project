# Boundary and regression tests


import random
import unittest
from collections import deque

from selection import deterministic_select, randomized_select
from structures import DynamicArray, Matrix, ArrayStack, ArrayQueue, SinglyLinkedList


class SelectionEdgeCases(unittest.TestCase):
    def test_rank_boundaries_and_distributions(self):
        cases = [
            [42], [2, 1], [1, 2], [7] * 101,
            list(range(101)), list(range(100, -1, -1)),
            [-10, -1, -10, 0, 10, 0],
            [0] * 100 + [1], [1] + [0] * 100,
            [10**30, -10**30, 0, 10**30],
            [1.5, -2.25, 0.0, 1.5],
        ]
        for values in cases:
            for k in range(1, len(values) + 1):
                expected = sorted(values)[k - 1]
                original = values[:]
                self.assertEqual(deterministic_select(values, k), expected)
                self.assertEqual(randomized_select(values, k, rng=random.Random(k)), expected)
                self.assertEqual(values, original)

    def test_group_boundaries_and_repeated_random_seeds(self):
        rng = random.Random(80)
        for n in (3, 4, 5, 6, 9, 10, 11, 14, 15, 16, 24, 25, 26, 49, 50, 51, 99, 100, 101):
            values = [rng.randint(-3, 3) for _ in range(n)]
            for k in (1, (n + 1) // 2, n):
                expected = sorted(values)[k - 1]
                self.assertEqual(deterministic_select(values, k), expected)
                for seed in range(5):
                    self.assertEqual(randomized_select(values, k, rng=random.Random(seed)), expected)

    def test_invalid_ranks(self):
        for select in (deterministic_select, randomized_select):
            for values, k in (([], 1), ([], 0), ([1], 0), ([1], -1), ([1], 2)):
                with self.subTest(select=select.__name__, k=k):
                    with self.assertRaises(ValueError):
                        select(values, k)
            for k in (True, False, 1.0, None, '1'):
                with self.assertRaises(TypeError):
                    select([1], k)


class StructureEdgeCases(unittest.TestCase):
    def test_dynamic_array_capacity_and_boundaries(self):
        a = DynamicArray[int](1)
        with self.assertRaises(IndexError):
            a.delete(0)
        a.insert(0, 10)
        a.insert(0, 5)
        a.insert(len(a), 20)
        self.assertEqual(a.to_list(), [5, 10, 20])
        for index in (-1, 4):
            with self.assertRaises(IndexError):
                a.insert(index, 0)
        for index in (-1, 3):
            with self.assertRaises(IndexError):
                _ = a[index]
        self.assertEqual([a.delete(0) for _ in range(3)], [5, 10, 20])
        self.assertGreaterEqual(a.capacity, 1)
        a.append(None)
        self.assertIsNone(a.delete(0))

    def test_matrix_empty_ragged_and_boundary_changes(self):
        with self.assertRaises(ValueError):
            Matrix([[1, 2], [3]])
        m = Matrix([[], []])
        self.assertEqual(m.shape, (2, 0))
        m.insert_column(0, [4, 5])
        self.assertEqual(m.to_list(), [[4], [5]])
        self.assertEqual(m.delete_column(0), [4, 5])
        self.assertEqual(m.delete_row(1), [])
        self.assertEqual(m.delete_row(0), [])
        self.assertEqual(m.shape, (0, 0))
        with self.assertRaises(IndexError):
            m.delete_row(0)

    def test_stack_empty_and_reuse(self):
        s = ArrayStack[int]()
        for operation in (s.pop, s.peek):
            with self.assertRaises(IndexError):
                operation()
        for _ in range(3):
            s.push(7)
            self.assertEqual(s.peek(), 7)
            self.assertEqual(s.pop(), 7)

    def test_queue_wraparound_growth_shrink_and_reuse(self):
        q = ArrayQueue[int](1)
        expected = deque()
        for i in range(1000):
            q.enqueue(i)
            expected.append(i)
            if i % 3 == 0:
                self.assertEqual(q.dequeue(), expected.popleft())
        while expected:
            self.assertEqual(q.dequeue(), expected.popleft())
        self.assertTrue(q.is_empty())
        q.enqueue(None)
        self.assertIsNone(q.dequeue())
        for operation in (q.dequeue, q.peek):
            with self.assertRaises(IndexError):
                operation()

    def test_linked_list_head_tail_and_duplicates(self):
        linked = SinglyLinkedList[int]()
        with self.assertRaises(IndexError):
            linked.delete(0)
        linked.append(2)
        linked.prepend(1)
        linked.append(2)
        self.assertEqual(linked.find(2), 1)
        self.assertEqual(linked.delete(2), 2)
        self.assertEqual(linked.delete(0), 1)
        self.assertEqual(linked.delete(0), 2)
        self.assertEqual(linked.to_list(), [])
        linked.append(99)
        self.assertEqual(linked.to_list(), [99])
        for index in (-1, 2):
            with self.assertRaises(IndexError):
                linked.insert(index, 0)


if __name__ == '__main__':
    unittest.main()
