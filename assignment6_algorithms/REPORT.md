# Assignment 6 Report: Medians, Order Statistics & Elementary Data Structures

## Overview and objectives

This project implements and evaluates two algorithms for the **k-th smallest element** of a collection, then builds five foundational data structures using explicit storage management and node links. The aim is to connect correctness arguments, asymptotic analysis, empirical evidence, and practical design trade-offs.

All algorithms are in Python and use only its standard library. Their public interfaces consistently use **1-based `k` for selection** and **0-based indices for collections**. Selection leaves the input unchanged. A `ValueError` is raised for an out-of-range `k`, and a `TypeError` for a noninteger `k`.

## Part 1 — Selection algorithms

### 1. Implementation and design

**Deterministic selection (`deterministic_select`)** uses the *median of medians* pivot strategy:

1. Divide the current active range into groups of five (the last may be shorter).
2. Sort each small group and record its median. Sorting a group of at most five is bounded by a constant cost.
3. Select the median of these medians recursively; use it as a pivot.
4. Perform an in-place Dutch-national-flag partition, producing regions with values below, equal to, and above the pivot.
5. Return an element in the equal region if its rank includes the target index. Otherwise, continue only in the required partition.

The median-finding procedure recursively uses the same deterministic selection routine on the temporary list of medians. While `k` is 1-based to callers, internal indices are zero-based.

**Randomized selection (`randomized_select`)** uses *randomized Quickselect*. It chooses a pivot at a uniformly random index in the active range, performs the same three-way partition, and iterates only into the side containing the target index. A supplied `random.Random(seed)` makes a run reproducible without modifying the global random generator.

**Correctness and duplicates.** A three-way partition maintains the invariant that all elements left of `lt` are smaller than the pivot, all values from `lt` through `gt` equal it, and those after `gt` are larger. If the target index lies in `[lt, gt]`, its order statistic is the pivot; otherwise it lies entirely in one remaining subrange. This is also why an all-equal input is processed in one partition instead of degenerating into quadratic behavior. Every iteration reduces the active range unless it returns, establishing termination. The input sequence is copied once by the public functions, preventing unexpected changes to callers' lists.

### 2. Time complexity

Let \(n\) be the current active input length.

**Deterministic median of medians.** There are \(\lceil n/5\rceil\) groups. Their constant-size sorting and the three-way partition together cost \(O(n)\). At least roughly half the group medians are no smaller than the chosen median of medians; each qualifying *full* group contributes at least three elements no smaller than the pivot. Symmetrically, many elements are no greater than the pivot. Ignoring a constant number of small groups, the larger recursive partition has size at most \(7n/10+O(1)\). The total work obeys

\[
T(n) \le T(\lceil n/5\rceil) + T(7n/10+O(1)) + cn.
\]

Since \(1/5 + 7/10 = 9/10 < 1\), substitution/induction (for sufficiently large \(n\), absorbing constant terms) yields **\(T(n)=O(n)\) in the worst case**. Selecting a k-th order statistic also needs to examine enough input data to establish its rank, giving a linear lower bound in the standard comparison setting; thus this algorithm is **\(\Theta(n)\)** worst-case. Its guarantee does not depend on original ordering or random choices.

**Randomized Quickselect.** Partitioning and pivot selection together cost \(O(n)\) per iteration. A uniformly chosen pivot has at least a 1/2 probability of lying in the middle half of the current ranks; when it does, at most 3/4 of the elements remain. The expected number of trials to obtain a constant-factor reduction is bounded by a constant. Summing expected work over decreasing range sizes gives

\[
E[T(n)] = O(n) + O(3n/4) + O((3/4)^2n) + \cdots = O(n).
\]

The number of trials is not fixed, so a sequence of very poor pivots can reduce the active range by only one element per iteration: \(n+(n-1)+\dots+1=\Theta(n^2)\) in the **worst case**. Randomization makes such behavior unlikely under independent uniform pivot selection, but does not make the worst-case bound linear.

| Algorithm | Best case (nontrivial n) | Expected / average | Worst case |
|---|---|---|---|
| Median of Medians | \(\Theta(n)\) | \(\Theta(n)\) | **\(\Theta(n)\)** |
| Randomized Quickselect | \(\Theta(n)\) | **\(\Theta(n)\)** over random pivots | \(\Theta(n^2)\) |

These bounds treat comparison, swaps, and small-group sorting as constant-time operations. Integer comparisons satisfy this assumption for fixed-size machine integers; comparisons of arbitrary large or complex Python objects can have additional costs.

### 3. Space complexity and overhead

- The public functions copy the input into an \(n\)-element working list, so **both use \(O(n)\) extra memory** as implemented. This is a deliberate no-side-effects design choice.
- Deterministic selection additionally materializes up to \(\lceil n/5\rceil\) medians at a time. Its nested median computations decrease geometrically, so temporary storage remains **\(O(n)\)** at peak; nested helper calls use **\(O(\log n)\)** call-stack frames for pivot computation. The main selection loop itself is iterative.
- Randomized selection uses an **iterative** loop and only constant-size index/pivot variables beyond its input copy, giving **\(O(1)\)** working space after that copy. An in-place caller-owned variant could eliminate the \(O(n)\) copying overhead but would mutate the supplied array.
- In Python, the deterministic method has larger constants from creating group slices, sorting every group, creating the medians list, and recursively selecting pivot medians. Quickselect mostly performs one partition per iteration and has lower bookkeeping cost.

### 4. Empirical evaluation

**Method.** The benchmark script generates four distributions: seeded random integers, sorted distinct integers, reverse-sorted distinct integers, and random values drawn from only ten keys (many duplicates). It computes the upper median (\(k=\lfloor n/2\rfloor+1\)) for arrays of 1,000, 5,000, 10,000, and 20,000 elements. For each condition it performs an untimed warm-up and seven measured trials; the results below are the **median of seven elapsed wall-clock times** in milliseconds. All answers are verified against `sorted(data)[k-1]`. Input construction and reference sorting are excluded from timing, while the one-time input copy within each selection function is included. Seeded randomized pivot generators are prepared outside timing; different repetitions use different deterministic seeds.

**Environment.** The provided benchmark output was generated on Linux x86-64 using **Python 3.13.5** in this execution environment, via `time.perf_counter_ns()`. The timings are machine-, interpreter-, and load-dependent and should not be interpreted as universal performance rankings.

**Recorded measurements:**

| Array size | Distribution | Median of Medians (ms) | Randomized Quickselect (ms) |
|---:|---|---:|---:|
| 1,000 | Random integers | 0.485 | 0.343 |
| 1,000 | Sorted ascending | 0.422 | 0.308 |
| 1,000 | Reverse sorted | 0.425 | 0.257 |
| 1,000 | Many duplicates (10 keys) | 0.174 | 0.159 |
| 5,000 | Random integers | 2.540 | 1.688 |
| 5,000 | Sorted ascending | 2.291 | 1.595 |
| 5,000 | Reverse sorted | 2.214 | 1.548 |
| 5,000 | Many duplicates (10 keys) | 0.917 | 0.971 |
| 10,000 | Random integers | 5.017 | 3.364 |
| 10,000 | Sorted ascending | 4.445 | 3.223 |
| 10,000 | Reverse sorted | 4.462 | 2.900 |
| 10,000 | Many duplicates (10 keys) | 1.814 | 1.792 |
| 20,000 | Random integers | 10.098 | 5.966 |
| 20,000 | Sorted ascending | 9.408 | 6.558 |
| 20,000 | Reverse sorted | 9.185 | 6.428 |
| 20,000 | Many duplicates (10 keys) | 4.093 | 4.912 |

**Observed behavior.** In the 20,000-element random case, Median of Medians required approximately **10.10 ms**, while Randomized Quickselect required **5.97 ms**. Randomized selection is usually faster for random and ordered input, consistent with its cheaper pivot selection. Sorted and reverse-sorted arrays do not reliably cause quadratic Quickselect behavior here, because pivots are chosen uniformly randomly rather than from a fixed endpoint. Duplicate-heavy arrays run quickly because three-way partitioning can discard many equal keys in a single step; in this case the deterministic implementation can sometimes be competitive or faster, depending on the run.

Across the full 1,000-to-20,000 size increase (a factor of 20), observed durations grow by factors on the order of twenty, although the exact ratios vary from run to run. This is consistent with the **linear or expected-linear** theoretical analysis but does not prove a bound on its own. Runtime measurements can be distorted by clock resolution, memory allocation, cache effects, garbage collection, interpreter overhead, random-pivot variation, and contention. Larger inputs and additional independently seeded trials could improve statistical confidence. The complete observations, including minimum and maximum trial times, are in `empirical_results.csv`; `benchmark.py` can regenerate them.

### 5. Practical uses of selection

Selection avoids sorting the entire array when only one order statistic is needed. Examples include median and percentile estimation for monitoring, finding the threshold between top-k and remaining items, rank-based filtering, and choosing a robust central estimate. The deterministic guarantee matters when predictable worst-case latency is essential or adversarial inputs are possible. Randomized Quickselect is usually preferable in ordinary analytical workloads when good expected performance and simpler pivot handling matter more than a strict worst-case limit.

## Part 2 — Elementary data structures

### 1. Implementations and invariants

**Dynamic array (`DynamicArray`).** A fixed-capacity Python list serves as raw storage; logical size is tracked separately. `insert` shifts entries to the right, `delete` shifts left, and indexing accesses an element directly. Capacity doubles when full and shrinks by half at or below one-quarter full, never below the original capacity. These policies keep append/remove-last amortized constant time and avoid resizing on every operation. We use Python's list only for fixed-capacity allocation and storage indexing, not Python's built-in list insertion/deletion routines.

**Matrix (`Matrix`).** A rectangular collection of `DynamicArray` rows. It supports cell get/set, entire row insert/delete, and column insert/delete. Row lengths are checked to preserve a uniform width. A matrix that has no rows has zero columns; users must insert at least one row before inserting a column. This is a row-major, dynamically resizable design, rather than a fixed-size numerical matrix.

**Array stack (`ArrayStack`).** Last-in-first-out operations `push`, `pop`, and `peek` use the last occupied position in a dynamic array. No search or shifting is needed for normal stack actions.

**Circular array queue (`ArrayQueue`).** First-in-first-out operations `enqueue`, `dequeue`, and `peek` use a circular buffer with a front index, size, and modular indexing. The queue grows/shrinks geometrically. Importantly, dequeueing does **not** shift all remaining elements; occasional buffer resizing is amortized across many operations.

**Singly linked list (`SinglyLinkedList`).** Each node contains a value and a reference to the next node. Head and tail pointers enable constant-time prepend and append, respectively. Index-based insertion/deletion, search (`find`), value access (`get`), and iteration/traversal are provided. When deleting the last node or the only node, tail pointers are updated to preserve invariants. The nodes are implemented with a slotted `dataclass` to reduce per-node object overhead relative to unslotted classes.

All structures reject out-of-bounds accesses; empty-stack and empty-queue removals raise `IndexError`. `None` can be stored as a normal element because occupancy is tracked independently of the storage slot's value.

### 2. Operation complexity

Let \(n\) be the number of stored elements. For a matrix, let \(r\) be its row count and \(c\) its column count. "Amort." means amortized over a sequence of operations; an individual capacity change can cost linear time.

| Structure | Operation | Time complexity | Why |
|---|---|---|---|
| Dynamic array | Access / update by index | **\(O(1)\)** | Direct offset lookup |
| Dynamic array | Append | **\(O(1)\) amort.**, \(O(n)\) worst | Occasional capacity expansion |
| Dynamic array | Insert / delete at front or middle | **\(O(n)\)** | Elements are shifted |
| Dynamic array | Delete last | **\(O(1)\) amort.**, \(O(n)\) worst | May shrink capacity |
| Matrix | Access / update a cell | **\(O(1)\)** | Two direct indexed accesses |
| Matrix | Insert row | **\(O(r+c)\)** worst | Build new row and shift row references |
| Matrix | Delete row | **\(O(r+c)\)** | Shift row references and export removed row |
| Matrix | Insert / delete column | **\(O(rc)\)** worst | Shift up to \(c\) entries in each of \(r\) rows |
| Array stack | Push / pop | **\(O(1)\) amort.** | Operate at dynamic-array end |
| Array stack | Peek | **\(O(1)\)** | Access last element |
| Circular array queue | Enqueue / dequeue | **\(O(1)\) amort.** | Modular indexing; occasional resize |
| Circular array queue | Peek | **\(O(1)\)** | Direct access to front |
| Singly linked list | Prepend / append | **\(O(1)\)** | Change head or tail references |
| Singly linked list | Delete head | **\(O(1)\)** | Advance head pointer |
| Singly linked list | Search / indexed access | **\(O(n)\)** | Follow links sequentially |
| Singly linked list | Insert / delete at arbitrary index | **\(O(n)\)** | Traverse to predecessor |
| Singly linked list | Traverse all values | **\(O(n)\)** | Visit each node once |

**Clarifications.** `Matrix.delete_row` returns a newly built standard Python list of the removed values, so its **full method** takes \(O(r+c)\) worst-case rather than only the \(O(r)\) cost of shifting the row references. `Matrix.delete_column` similarly returns the removed values but remains \(O(rc)\) overall. For a single-row matrix, `insert_column` costs \(O(c)\); its general bound is \(O(rc)\). Allocating a new matrix with \(rc\) elements takes \(O(rc)\). Creating a dynamic array or empty stack/queue/list is \(O(1)\).

### 3. Space complexity and memory considerations

| Structure | Space |
|---|---|
| Dynamic array | \(O(n)\) allocated element slots (with spare capacity due to geometric growth) |
| Rectangular matrix | \(O(rc+r)\), usually stated \(O(rc)\) for nonempty width, plus row objects |
| Array stack | \(O(n)\) |
| Circular array queue | \(O(n)\) |
| Singly linked list | \(O(n)\) nodes, each with value and next reference |

Resizable arrays reserve unused capacity to avoid frequent reallocation; they have excellent spatial locality and often outperform linked nodes in real Python even when asymptotic bounds are similar. Linked lists allocate separately for every node and store references, adding memory and allocation overhead but avoiding shifts when inserting at a **known** position (including the head). Arrays are typically preferable when access by numeric index is frequent, while linked lists can be useful when a program already holds node references and often splices or removes nodes (this specific public singly linked list exposes **indices**, not external node handles, so indexed splicing still requires traversal).

### 4. Arrays versus linked lists for stacks and queues

For a **stack**, dynamic-array storage usually has the best practical trade-off: append and remove-last are amortized \(O(1)\), indexing the top is immediate, cache locality is strong, and there is no node allocation per push. A linked stack can achieve worst-case \(O(1)\) push/pop at the head without resizing pauses, but each pushed item requires a new linked node.

For a **queue**, an array implementation that removes position zero by shifting items would take \(O(n)\) per dequeue. The implemented **circular array queue** avoids this problem and offers amortized \(O(1)\) enqueue/dequeue. A linked queue with head and tail pointers also offers \(O(1)\) worst-case enqueue/dequeue, but normally has more per-element memory overhead and poorer locality. If strict worst-case time is more important than compactness, linked queue operations can be attractive; if throughput and memory locality matter, the circular array is often better.

### 5. Real-world applications and preferences

- **Dynamic arrays**: dynamic collections such as product lists, timestamp samples, and indexed tables. Prefer them when fast random access matters and most updates are at the end.
- **Matrices**: game boards, grid-based simulation, small image-like data, or adjacency tables. Prefer fixed contiguous numerical matrices in specialized libraries for large numeric workloads; this implementation prioritizes educational clarity and insertion/deletion functionality.
- **Stacks**: undo histories, expression parsing, browser navigation, and depth-first search. LIFO naturally models nested operations.
- **Queues**: job scheduling, print spooling, breadth-first search, and request buffering. FIFO preserves processing order.
- **Singly linked lists**: node-based pipelines, educational memory models, and situations that insert/remove at the front frequently without requiring indexing. A dynamic array is often more memory-efficient for many typical Python collections.

### 6. Testing and limitations

The `unittest` suite covers both selection functions on empty/out-of-range queries, sorted and reverse-sorted arrays, negative integers, duplicate-heavy data, and comparable strings. Randomized property-style cases cross-check against sorting. Data-structure tests check capacity changes, positional insertion/deletion, circular-buffer wraparound, empty-operation errors, matrix shape consistency, `None` values, and linked-list head/tail transitions. **All 19 tests passed** in the local verification run.

The project intentionally does not implement optional rooted trees. Generic type annotations are for clarity; Python's runtime does not enforce all type constraints. This is educational code, not a drop-in replacement for optimized numerical libraries or production concurrency-safe queues. Thread synchronization, concurrency, and persistent storage are outside the assignment's scope.

## Conclusion

Median of Medians offers a reliable worst-case linear bound at the cost of extra pivot work, whereas randomized Quickselect is typically faster and simpler in expectation but admits quadratic worst-case behavior. Among elementary structures, operation patterns dictate the best choice: arrays for indexing and locality, stacks for LIFO, circular queues for FIFO, matrices for row/column organization, and linked nodes for pointer-oriented traversal and head operations. Actual measured times reinforce the theory without replacing asymptotic reasoning.

## Reproducibility

```bash
python -m unittest discover -s tests -v
python benchmark.py --sizes 1000 5000 10000 20000 --repeats 7 --seed 42 --output empirical_results.csv
```

The CSV file is the raw tabular artifact for every experimental condition, with per-condition median, minimum, and maximum times. See `README.md` for repository setup and GitHub publishing instructions.

## Additional edge-case verification (in response to prior grading feedback)

The earlier rubric concerned Quicksort, not the selection algorithms required here. To prevent similar boundary-condition deductions, `tests/test_edge_cases.py` adds explicit regression coverage for:

- **Selection:** empty input, invalid ranks (`k=0`, negative, larger than `n`), non-integer ranks including booleans, single/two-element inputs, first/middle/last ranks, all-equal values, repeated values, ascending/descending data, negative and very large integers, floats, group-of-five boundaries, multiple random seeds, and preservation of caller input.
- **Dynamic array:** zero elements, insertion at front/end, invalid indices, resizing down to minimum capacity, and stored `None`.
- **Matrix:** ragged rows rejected, zero-width rows, column insert/delete at the boundary, deleting the last row, and invalid operations on an empty matrix.
- **Stack:** empty pop/peek and reuse after draining.
- **Circular queue:** wraparound, growth, shrinking, FIFO after many operations, stored `None`, and empty dequeue/peek.
- **Linked list:** empty deletion, first/last-node removal, duplicates, tail repair after draining, and invalid insertion positions.

**Verification:** `py -m unittest discover -s tests -v` completed successfully on Windows with Python 3.14.7; **19 tests passed**. Pylance workspace diagnostics found no issues, and Pylance syntax checks found no errors in `selection.py`, `structures.py`, or `benchmark.py`. This expands automated coverage, but does not guarantee a particular rubric grade.

**Input contract:** Selection accepts a nonempty finite sequence of mutually comparable values and uses one-based integer `k`. NaN and mixed incomparable Python types are outside the supported ordering contract; Python's comparisons do not define a total order for them. The algorithms are selection methods, not Quicksort implementations.
