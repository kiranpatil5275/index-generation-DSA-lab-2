"""
benchmark.py - generates the 6 big test files, times Trie / BST / Dict
and plots the results with Matplotlib.

Usage:
    python benchmark.py            # full run (>= 1,000,000 words per file)
    python benchmark.py --quick    # small run to test quickly
"""
import random
import sys
import time

import matplotlib
matplotlib.use("Agg")               # save to file; works without a display
import matplotlib.pyplot as plt

from index_generator import METHODS, build_index, read_lines

# printable ASCII (33..126) except the separators  . , : ;
CHARS = [chr(c) for c in range(33, 127) if chr(c) not in ".,:;"]


def make_test_file(path, distinct, total_words, words_per_line=10):
    """Write a file with exactly `distinct` different words and `total_words`
    words in all (so words repeat). Returns the list of distinct words."""
    words = set()
    while len(words) < distinct:
        length = random.randint(4, 8)
        words.add("".join(random.choices(CHARS, k=length)))
    words = list(words)
    # every distinct word once, the rest are random repeats
    all_words = words + random.choices(words, k=total_words - distinct)
    random.shuffle(all_words)
    with open(path, "w") as f:
        for i in range(0, len(all_words), words_per_line):
            f.write(" ".join(all_words[i:i + words_per_line]) + "\n")
    return words


def timed(func):
    start = time.perf_counter()
    func()
    return time.perf_counter() - start


def main():
    quick = "--quick" in sys.argv
    sizes = [1000, 5000, 10000, 50000, 100000, 500000]
    total, n_search = 1_000_000, 100_000
    if quick:
        sizes, total, n_search = [100, 500, 1000, 5000, 10000, 50000], 100_000, 10_000

    results = {m: {"build": [], "search": [], "print": []} for m in METHODS}

    for d in sizes:
        path = f"test_{d}.txt"
        print(f"\n=== {d} distinct words: generating {path} ...")
        words = make_test_file(path, d, total)
        lines = read_lines(path)                     # file read is not timed
        queries = random.choices(words, k=n_search)  # 100000 random words

        for m in METHODS:
            holder = {}
            t_build = timed(lambda: holder.update(idx=build_index(lines, m)))
            idx = holder["idx"]
            t_search = timed(lambda: [idx.search(w) for w in queries])
            t_print = timed(lambda: idx.write(f"index_{m}_{d}.txt"))
            results[m]["build"].append(t_build)
            results[m]["search"].append(t_search)
            results[m]["print"].append(t_print)
            print(f"{m:5s} build={t_build:7.2f}s search={t_search:7.2f}s print={t_print:7.2f}s")
            del idx, holder

    # ---- plotting: one graph per action ----
    titles = {"build": "Construction time", "search": "Search time (random words)",
                "print": "Printing time (sorted index)"}
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    for ax, action in zip(axes, titles):
        for m in METHODS:
            ax.plot(sizes, results[m][action], marker="o", label=m)
        ax.set_title(titles[action])
        ax.set_xlabel("Number of distinct words")
        ax.set_ylabel("Time (seconds)")
        ax.set_xscale("log")
        ax.grid(True)
        ax.legend()
    plt.tight_layout()
    plt.savefig("performance1.png", dpi=120)
    print("\nGraph saved as performance1.png")


if __name__ == "__main__":
    main()
