# Order-statistic selection using deterministic and randomized pivots.

# Both public functions use ONE-BASED k and leave the caller's input unchanged.
# Duplicates are handled by three-way (less/equal/greater) partitioning.


from __future__ import annotations

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


def _validate(values: Sequence[T], k: int) -> None:
    """Reject invalid order statistics before making a working copy."""
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be an integer (1-based)")
    if not 1 <= k <= len(values):
        raise ValueError("k must satisfy 1 <= k <= len(values)")


def _partition_three_way(
    a: list[T], left: int, right: int, pivot: T
) -> tuple[int, int]:
    """Partition a[left:right+1] in-place; return bounds of == pivot.

    After partition, [left, lt) < pivot, [lt, gt] == pivot,
    and (gt, right] > pivot. Works when many keys are equal.
    """
    lt, i, gt = left, left, right
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[gt], a[i] = a[i], a[gt]
            gt -= 1
        else:
            i += 1
    return lt, gt


def _median_of_medians(a: list[T], left: int, right: int) -> T:
    """Select a 'good' pivot from groups of at most five elements.

    Groups are locally sorted (constant-time per group). The middle
    median of those group medians is selected recursively.
    """
    count = right - left + 1
    if count <= 5:
        small = sorted(a[left : right + 1])
        return small[count // 2]

    medians: list[T] = []
    for start in range(left, right + 1, 5):
        group = sorted(a[start : min(start + 5, right + 1)])
        medians.append(group[len(group) // 2])

    return _select_in_place(medians, 0, len(medians) - 1, len(medians) // 2)


def _select_in_place(a: list[T], left: int, right: int, target: int) -> T:
    """Select the absolute, zero-based target within the given interval."""
    while left < right:
        pivot = _median_of_medians(a, left, right)
        lt, gt = _partition_three_way(a, left, right, pivot)
        if target < lt:
            right = lt - 1
        elif target > gt:
            left = gt + 1
        else:
            return a[target]
    return a[left]


def deterministic_select(values: Sequence[T], k: int) -> T:
    """Return the k-th smallest value, worst-case O(n) time.

    k is 1-based. Works with comparable values (including duplicates),
    and does not modify `values`. Uses O(n) auxiliary space because of
    the input copy and temporary lists of group medians.
    """
    _validate(values, k)
    a = list(values)
    return _select_in_place(a, 0, len(a) - 1, k - 1)


def randomized_select(
    values: Sequence[T], k: int, *, rng: random.Random | None = None
) -> T:
    """Return the k-th smallest value, expected O(n) time.

    Chooses a uniformly random pivot from the current active interval.
    Worst-case time is O(n^2), though that is very unlikely with random
    pivots; three-way partitioning handles duplicates efficiently.
    Iterative selection uses O(1) additional workspace beyond the O(n)
    input copy. Pass a seeded `random.Random` for reproducibility.
    """
    _validate(values, k)
    a = list(values)
    generator = rng if rng is not None else random.Random()
    left, right, target = 0, len(a) - 1, k - 1
    while left < right:
        pivot = a[generator.randrange(left, right + 1)]
        lt, gt = _partition_three_way(a, left, right, pivot)
        if target < lt:
            right = lt - 1
        elif target > gt:
            left = gt + 1
        else:
            return a[target]
    return a[left]


if __name__ == "__main__":
    sample = [9, 2, 7, 2, 4, 8, 1]
    for k_value in (1, 4, len(sample)):
        print(f"k={k_value}: deterministic={deterministic_select(sample, k_value)}, "
              f"randomized={randomized_select(sample, k_value)}")
