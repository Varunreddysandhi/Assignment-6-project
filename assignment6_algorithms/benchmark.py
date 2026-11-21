"""Reproducible wall-clock comparison of deterministic and randomized select.

Times use perf_counter_ns, measure selection including its input copy, and
exclude input generation, sorting for verification, and CSV writing.
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
import time
from pathlib import Path

from selection import deterministic_select, randomized_select


def make_data(distribution: str, size: int, seed: int) -> list[int]:
    if distribution == "random":
        rng = random.Random(seed)
        return [rng.randrange(-10 * size, 10 * size + 1) for _ in range(size)]
    if distribution == "sorted":
        return list(range(size))
    if distribution == "reverse_sorted":
        return list(range(size - 1, -1, -1))
    if distribution == "many_duplicates":
        rng = random.Random(seed)
        return [rng.randrange(10) for _ in range(size)]
    raise ValueError(f"unknown distribution: {distribution}")


def benchmark(sizes: list[int], repeats: int, seed: int) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for size in sizes:
        if size < 1:
            raise ValueError("all sizes must be positive")
        for distribution in ("random", "sorted", "reverse_sorted", "many_duplicates"):
            data = make_data(distribution, size, seed + size)
            k = size // 2 + 1  # 1-based upper median for even sizes.
            correct = sorted(data)[k - 1]
            # Warm up each code path outside measured repetitions.
            assert deterministic_select(data, k) == correct
            assert randomized_select(data, k, rng=random.Random(seed)) == correct
            for name, algorithm in (
                ("median_of_medians", deterministic_select),
                ("randomized_quickselect", randomized_select),
            ):
                samples_ms = []
                for repeat in range(repeats):
                    # Prepare the seeded generator before timing the selection.
                    trial_rng = random.Random(seed + repeat) if name != "median_of_medians" else None
                    start = time.perf_counter_ns()
                    if name == "median_of_medians":
                        answer = algorithm(data, k)
                    else:
                        answer = algorithm(data, k, rng=trial_rng)
                    duration_ms = (time.perf_counter_ns() - start) / 1_000_000
                    if answer != correct:
                        raise AssertionError(f"incorrect answer: {name}, {distribution}, {size}")
                    samples_ms.append(duration_ms)
                results.append({
                    "size": size,
                    "distribution": distribution,
                    "algorithm": name,
                    "repeats": repeats,
                    "median_ms": round(statistics.median(samples_ms), 6),
                    "min_ms": round(min(samples_ms), 6),
                    "max_ms": round(max(samples_ms), 6),
                })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[1000, 5000, 10000, 20000])
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("empirical_results.csv"))
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    rows = benchmark(args.sizes, args.repeats, args.seed)
    with args.output.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=[
            "size", "distribution", "algorithm", "repeats", "median_ms", "min_ms", "max_ms"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    print("size       distribution        median-of-medians (ms)  randomized (ms)")
    for i in range(0, len(rows), 2):
        a, b = rows[i : i + 2]
        print(f"{a['size']:<10} {a['distribution']:<19} {a['median_ms']:>15.4f} "
              f"{b['median_ms']:>18.4f}")


if __name__ == "__main__":
    main()
