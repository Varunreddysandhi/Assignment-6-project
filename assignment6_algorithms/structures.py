"""Elementary data structures implemented with explicit storage/links.

Zero-based indices are used throughout. Negative indices are rejected.
No list.append/pop/insert is used to implement the core data structures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, Sequence, TypeVar, cast

T = TypeVar("T")


class DynamicArray(Generic[T]):
    """Resizable array with manual indexing, shifting, and capacity growth.

    Invariant: 0 <= size <= capacity. All used entries occupy [0, size).
    Doubling on growth and halving at quarter capacity give amortized
    O(1) append and remove-last, while insert/delete-middle are O(n).
    """

    def __init__(self, capacity: int = 4) -> None:
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self._min_capacity = capacity
        self._data: list[Optional[T]] = [None] * capacity
        self._size = 0

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._data)

    def _check_index(self, index: int) -> None:
        if not 0 <= index < self._size:
            raise IndexError("array index out of range")

    def _resize(self, new_capacity: int) -> None:
        replacement: list[Optional[T]] = [None] * new_capacity
        for i in range(self._size):
            replacement[i] = self._data[i]
        self._data = replacement

    def __getitem__(self, index: int) -> T:
        self._check_index(index)
        return cast(T, self._data[index])

    def __setitem__(self, index: int, value: T) -> None:
        self._check_index(index)
        self._data[index] = value

    def insert(self, index: int, value: T) -> None:
        if not 0 <= index <= self._size:
            raise IndexError("insertion index out of range")
        if self._size == self.capacity:
            self._resize(2 * self.capacity)
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def append(self, value: T) -> None:
        self.insert(self._size, value)

    def delete(self, index: int) -> T:
        self._check_index(index)
        removed = cast(T, self._data[index])
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._size -= 1
        self._data[self._size] = None  # Release unused reference.
        if self.capacity > self._min_capacity and self._size <= self.capacity // 4:
            self._resize(max(self._min_capacity, self.capacity // 2))
        return removed

    def __iter__(self) -> Iterator[T]:
        for i in range(self._size):
            yield cast(T, self._data[i])

    def to_list(self) -> list[T]:
        return list(self)


class Matrix(Generic[T]):
    """Rectangular row-major matrix composed of DynamicArray rows.

    Access/assignment are O(1). Inserting/deleting a row takes O(r+c)
    worst-case; inserting/deleting a column takes O(r*c) worst-case.
    A matrix without rows has zero columns until its first row is added.
    """

    def __init__(self, rows: Sequence[Sequence[T]] = ()) -> None:
        self._rows: DynamicArray[DynamicArray[T]] = DynamicArray()
        self._columns = 0
        for row in rows:
            self.insert_row(len(self._rows), row)

    @property
    def shape(self) -> tuple[int, int]:
        return len(self._rows), self._columns

    def _check_coordinates(self, row: int, column: int) -> None:
        if not (0 <= row < len(self._rows) and 0 <= column < self._columns):
            raise IndexError("matrix coordinates out of range")

    def get(self, row: int, column: int) -> T:
        self._check_coordinates(row, column)
        return self._rows[row][column]

    def set(self, row: int, column: int, value: T) -> None:
        self._check_coordinates(row, column)
        self._rows[row][column] = value

    def insert_row(self, index: int, values: Sequence[T]) -> None:
        if not 0 <= index <= len(self._rows):
            raise IndexError("row insertion index out of range")
        if len(self._rows) and len(values) != self._columns:
            raise ValueError("row width must match matrix width")
        new_row: DynamicArray[T] = DynamicArray()
        for value in values:
            new_row.append(value)
        self._rows.insert(index, new_row)
        if len(self._rows) == 1:
            self._columns = len(values)

    def delete_row(self, index: int) -> list[T]:
        row = self._rows.delete(index).to_list()
        if len(self._rows) == 0:
            self._columns = 0
        return row

    def insert_column(self, index: int, values: Sequence[T]) -> None:
        r, c = self.shape
        if r == 0:
            raise ValueError("insert a row before inserting a column")
        if not 0 <= index <= c:
            raise IndexError("column insertion index out of range")
        if len(values) != r:
            raise ValueError("column height must match matrix height")
        for i, value in enumerate(values):
            self._rows[i].insert(index, value)
        self._columns += 1

    def delete_column(self, index: int) -> list[T]:
        r, c = self.shape
        if not 0 <= index < c:
            raise IndexError("column deletion index out of range")
        removed = [self._rows[i].delete(index) for i in range(r)]
        self._columns -= 1
        return removed

    def to_list(self) -> list[list[T]]:
        return [row.to_list() for row in self._rows]


class ArrayStack(Generic[T]):
    """Last-in-first-out stack backed by a dynamic array."""

    def __init__(self) -> None:
        self._items: DynamicArray[T] = DynamicArray()

    def __len__(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return len(self) == 0

    def push(self, value: T) -> None:
        self._items.append(value)

    def pop(self) -> T:
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.delete(len(self._items) - 1)

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[len(self._items) - 1]


class ArrayQueue(Generic[T]):
    """First-in-first-out circular-buffer queue (no shifting on dequeue).

    Enqueue/dequeue are amortized O(1), peek is O(1). Dynamic doubling
    and quarter-full shrinking prevent O(n) shifts per dequeue.
    """

    def __init__(self, capacity: int = 4) -> None:
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self._min_capacity = capacity
        self._buffer: list[Optional[T]] = [None] * capacity
        self._front = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def _resize(self, capacity: int) -> None:
        new_buffer: list[Optional[T]] = [None] * capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[(self._front + i) % len(self._buffer)]
        self._buffer = new_buffer
        self._front = 0

    def enqueue(self, value: T) -> None:
        if self._size == len(self._buffer):
            self._resize(2 * len(self._buffer))
        end = (self._front + self._size) % len(self._buffer)
        self._buffer[end] = value
        self._size += 1

    def dequeue(self) -> T:
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        value = cast(T, self._buffer[self._front])
        self._buffer[self._front] = None
        self._front = (self._front + 1) % len(self._buffer)
        self._size -= 1
        if len(self._buffer) > self._min_capacity and self._size <= len(self._buffer) // 4:
            self._resize(max(self._min_capacity, len(self._buffer) // 2))
        return value

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return cast(T, self._buffer[self._front])

    def to_list(self) -> list[T]:
        return [cast(T, self._buffer[(self._front + i) % len(self._buffer)])
                for i in range(self._size)]


@dataclass(slots=True)
class _Node(Generic[T]):
    value: T
    next: Optional[_Node[T]] = None


class SinglyLinkedList(Generic[T]):
    """Singly linked list with a head and tail pointer.

    Prepend and append are O(1). Access by index, find, and deletion
    from arbitrary positions are O(n). Traversal is O(n).
    """

    def __init__(self) -> None:
        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def prepend(self, value: T) -> None:
        node = _Node(value, self._head)
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def append(self, value: T) -> None:
        node = _Node(value)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def _node_at(self, index: int) -> _Node[T]:
        if not 0 <= index < self._size:
            raise IndexError("linked-list index out of range")
        current = self._head
        for _ in range(index):
            assert current is not None
            current = current.next
        assert current is not None
        return current

    def get(self, index: int) -> T:
        return self._node_at(index).value

    def insert(self, index: int, value: T) -> None:
        if not 0 <= index <= self._size:
            raise IndexError("linked-list insertion index out of range")
        if index == 0:
            self.prepend(value)
        elif index == self._size:
            self.append(value)
        else:
            previous = self._node_at(index - 1)
            previous.next = _Node(value, previous.next)
            self._size += 1

    def delete(self, index: int) -> T:
        if not 0 <= index < self._size:
            raise IndexError("linked-list deletion index out of range")
        if index == 0:
            assert self._head is not None
            removed = self._head
            self._head = removed.next
            if self._head is None:
                self._tail = None
        else:
            previous = self._node_at(index - 1)
            assert previous.next is not None
            removed = previous.next
            previous.next = removed.next
            if previous.next is None:
                self._tail = previous
        self._size -= 1
        return removed.value

    def find(self, value: T) -> int:
        """Return index of first equal value, or -1 if not found."""
        for index, item in enumerate(self):
            if item == value:
                return index
        return -1

    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def to_list(self) -> list[T]:
        return list(self)


if __name__ == "__main__":
    items = DynamicArray[int]()
    items.append(10)
    items.insert(0, 5)
    print("DynamicArray:", items.to_list())
    grid = Matrix([[1, 2], [3, 4]])
    grid.insert_column(1, [9, 8])
    print("Matrix:", grid.to_list())
    stack = ArrayStack[int]()
    stack.push(1)
    stack.push(2)
    print("Stack pop:", stack.pop())
    queue = ArrayQueue[int]()
    queue.enqueue(1)
    queue.enqueue(2)
    print("Queue dequeue:", queue.dequeue())
    linked = SinglyLinkedList[int]()
    linked.append(2)
    linked.prepend(1)
    print("Linked list:", linked.to_list())
