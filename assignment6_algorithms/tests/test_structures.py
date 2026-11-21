# Functional and differential tests for manual data structures.

from collections import deque
import random
import unittest

from structures import ArrayQueue, ArrayStack, DynamicArray, Matrix, SinglyLinkedList


class DynamicArrayTests(unittest.TestCase):
    def test_insert_delete_access_and_resize(self) -> None:
        arr = DynamicArray[int]()
        reference: list[int] = []
        rng = random.Random(99)
        for _ in range(500):
            if not reference or rng.random() < 0.65:
                index = rng.randrange(len(reference) + 1)
                value = rng.randrange(500)
                reference.insert(index, value)
                arr.insert(index, value)
            else:
                index = rng.randrange(len(reference))
                self.assertEqual(arr.delete(index), reference.pop(index))
            self.assertEqual(arr.to_list(), reference)
            self.assertGreaterEqual(arr.capacity, len(arr))
        for i in range(len(reference)):
            arr[i] = -i
            reference[i] = -i
        self.assertEqual(arr.to_list(), reference)
        with self.assertRaises(IndexError):
            _ = arr[-1]
        with self.assertRaises(IndexError):
            arr.delete(len(arr))
        with self.assertRaises(ValueError):
            DynamicArray(0)

    def test_none_values(self) -> None:
        arr = DynamicArray[object]()
        arr.append(None)
        arr.append('x')
        self.assertEqual(arr.delete(0), None)
        self.assertEqual(arr.to_list(), ['x'])


class MatrixTests(unittest.TestCase):
    def test_rows_columns_access_and_dimensions(self) -> None:
        m = Matrix([[1, 2], [3, 4]])
        self.assertEqual(m.shape, (2, 2))
        self.assertEqual(m.get(1, 1), 4)
        m.set(0, 1, 6)
        m.insert_column(1, [8, 9])
        self.assertEqual(m.to_list(), [[1, 8, 6], [3, 9, 4]])
        self.assertEqual(m.delete_column(1), [8, 9])
        m.insert_row(1, [7, 7])
        self.assertEqual(m.to_list(), [[1, 6], [7, 7], [3, 4]])
        self.assertEqual(m.delete_row(0), [1, 6])
        self.assertEqual(m.delete_row(0), [7, 7])
        self.assertEqual(m.delete_row(0), [3, 4])
        self.assertEqual(m.shape, (0, 0))
        m.insert_row(0, [1])
        self.assertEqual(m.shape, (1, 1))
        with self.assertRaises(ValueError):
            m.insert_row(0, [1, 2])
        with self.assertRaises(ValueError):
            m.insert_column(0, [1, 2])

    def test_empty_matrix(self) -> None:
        m = Matrix()
        with self.assertRaises(ValueError):
            m.insert_column(0, [])
        with self.assertRaises(IndexError):
            m.get(0, 0)


class StackQueueTests(unittest.TestCase):
    def test_stack(self) -> None:
        stack = ArrayStack[int]()
        self.assertTrue(stack.is_empty())
        with self.assertRaises(IndexError):
            stack.pop()
        for n in range(250):
            stack.push(n)
            self.assertEqual(stack.peek(), n)
        for n in reversed(range(250)):
            self.assertEqual(stack.pop(), n)
        self.assertTrue(stack.is_empty())

    def test_queue_wraparound_and_resize(self) -> None:
        queue = ArrayQueue[object](capacity=2)
        reference: deque[object] = deque()
        rng = random.Random(101)
        for i in range(1800):
            if not reference or rng.random() < 0.62:
                value = None if i % 17 == 0 else i
                queue.enqueue(value)
                reference.append(value)
            else:
                self.assertEqual(queue.dequeue(), reference.popleft())
            self.assertEqual(queue.to_list(), list(reference))
            self.assertEqual(len(queue), len(reference))
            if reference:
                self.assertEqual(queue.peek(), reference[0])
        while reference:
            self.assertEqual(queue.dequeue(), reference.popleft())
        with self.assertRaises(IndexError):
            queue.dequeue()
        with self.assertRaises(IndexError):
            queue.peek()


class LinkedListTests(unittest.TestCase):
    def test_traversal_insertion_deletion(self) -> None:
        linked = SinglyLinkedList[int]()
        reference: list[int] = []
        rng = random.Random(22)
        for _ in range(600):
            if not reference or rng.random() < 0.65:
                pos = rng.randrange(len(reference) + 1)
                value = rng.randrange(30)
                linked.insert(pos, value)
                reference.insert(pos, value)
            else:
                pos = rng.randrange(len(reference))
                self.assertEqual(linked.delete(pos), reference.pop(pos))
            self.assertEqual(linked.to_list(), reference)
            self.assertEqual(len(linked), len(reference))
        if reference:
            self.assertEqual(linked.get(0), reference[0])
        self.assertEqual(linked.find(-999), -1)
        with self.assertRaises(IndexError):
            linked.get(-1)
        with self.assertRaises(IndexError):
            linked.delete(len(linked))
        while len(linked):
            linked.delete(0)
        linked.append(123)
        self.assertEqual(linked.to_list(), [123])
        linked.prepend(9)
        self.assertEqual(linked.to_list(), [9, 123])


if __name__ == '__main__':
    unittest.main()
