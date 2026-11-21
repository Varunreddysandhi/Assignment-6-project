# Assignment 6 — Medians, Order Statistics & Elementary Data Structures

This repository contains runnable Python implementations, tests, reproducible selection benchmarks, and an analysis report for both parts of Assignment 6. It uses only the Python standard library (Python **3.10+** recommended).

## Project contents

| File | Purpose |
|---|---|
| `selection.py` | Worst-case linear-time median-of-medians selection and expected linear-time randomized Quickselect |
| `structures.py` | Dynamic array, rectangular matrix, array-based stack, circular-buffer queue, singly linked list |
| `benchmark.py` | Timed comparison on random, sorted, reverse-sorted, and duplicate-heavy arrays |
| `empirical_results.csv` | Recorded empirical results from the benchmark run described in the report |
| `REPORT.md` | Correctness, design choices, complexities, experimental results, and applications |
| `tests/` | Standard-library `unittest` test suite |

## Run the code

From the repository root:

```bash
python selection.py
python structures.py
python -m unittest discover -s tests -v
```

Reproduce or expand the benchmarks:

```bash
python benchmark.py --sizes 1000 5000 10000 20000 --repeats 7 --seed 42 --output empirical_results.csv
```

The benchmark checks each answer against sorting, reports the **median** elapsed time across repetitions in milliseconds, and includes copying input data in the timing. Your machine's times will differ.

## Example usage

```python
from selection import deterministic_select, randomized_select
from structures import DynamicArray, Matrix, ArrayStack, ArrayQueue, SinglyLinkedList

values = [8, 3, 3, 6, 1]
print(deterministic_select(values, 3))  # 3: third smallest (1-based k)
print(randomized_select(values, 5))     # 8

arr = DynamicArray[int]()
arr.append(10)
arr.insert(0, 7)
print(arr.to_list())  # [7, 10]

matrix = Matrix([[1, 2], [3, 4]])
matrix.insert_column(1, [9, 8])
print(matrix.to_list())  # [[1, 9, 2], [3, 8, 4]]

stack = ArrayStack[str]()
stack.push('first')
stack.push('last')
print(stack.pop())  # 'last'

queue = ArrayQueue[str]()
queue.enqueue('first')
queue.enqueue('next')
print(queue.dequeue())  # 'first'

linked = SinglyLinkedList[str]()
linked.append('middle')
linked.prepend('start')
print(linked.to_list())  # ['start', 'middle']
```

## Main findings

- Median of medians guarantees **O(n)** worst-case selection time using groups of five and three-way partitioning; the readable Python implementation incurs noticeable constant-factor overhead.
- Randomized Quickselect runs in **expected O(n)** time (worst case **O(n²)**) and typically has lower overhead in these experiments.
- Dynamic arrays provide **O(1)** indexing and amortized **O(1)** append; inserting in the middle costs **O(n)**.
- Array stacks and circular-buffer array queues support amortized **O(1)** operations; singly linked lists enable **O(1)** insert/remove at the head with **O(n)** indexing.

See [REPORT.md](REPORT.md) for details and experiment context.

## Publish to GitHub

Create a new empty GitHub repository, then from this folder run:

```bash
git init
git add .
git commit -m "Implement Assignment 6 algorithms and structures"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with your actual GitHub details. Submit the link to your own repository as required by the assignment. No repository is created or uploaded by the files in this archive.

## Edge-case tests

The `tests/test_edge_cases.py` module adds regression tests for rank boundaries, duplicate-heavy arrays, sorted/reverse-sorted inputs, group-of-five boundaries, multiple randomized pivots, and empty/resize/wraparound conditions for the data structures. Run all **19** tests with:

```bash
python -m unittest discover -s tests -v
```

The selection functions require a nonempty sequence of mutually comparable values and a one-based integer `k`. NaN and incomparable mixed types are not supported.

## Project audit status

The project was checked on Windows with Python 3.14.7:

- `py -m unittest discover -s tests -v` — **19 tests passed**
- Pylance workspace diagnostics — **no issues reported**
- Pylance syntax checks for `selection.py`, `structures.py`, and `benchmark.py` — **no syntax errors**

No source-code changes were required. Documentation was updated to report the correct suite size and local verification environment. The recorded benchmark values in `empirical_results.csv` remain the prior reproducible Linux/Python 3.13.5 measurements documented in `REPORT.md`; they were not replaced with a different machine's run.
