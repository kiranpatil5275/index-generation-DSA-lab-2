# Design Explanation – Index Generation

## Goal
Read a text file, find all words, and write a table of every word (in ASCII
lexicographic order) with the line numbers where it occurs.

## Files
- `index_generator.py` – the utility (Trie, BST, Dictionary versions)
- `benchmark.py` – makes the 6 big test files, times the 3 versions, plots graphs
- `sample.txt` – small test file

## How it works
1. **Reading words**: the file is read line by line (so we know the line number).
   Each line is split on blanks, tab, `.` `,` `:` `;` using one regular expression.
   Any other printable ASCII character is part of a word.
2. **Line numbers**: each word stores its line numbers in a **linked-list queue**
   (`LineQueue`) with `head` and `tail`, so adding a new line number is O(1).
   If a word repeats on the same line, the line number is stored only once.
3. **Trie**: one node per character; `children` is a dict {char: node}. A node whose
   `lines` is not None marks the end of a word. Printing = depth-first walk,
   visiting children in sorted order.
4. **BST**: each node holds a word, its `LineQueue`, `left`, `right`. Smaller words go
   left, bigger go right, equal words just add the line number. Printing =
   in-order traversal (left, node, right). Insert/traverse are iterative.
5. **Dictionary**: `word -> LineQueue`. Python dicts are unordered, so keys are
   sorted just before printing.
6. All three classes have the same methods: `add`, `search`, `write`.

## Complexity (n = distinct words, L = word length)
| Version | Insert / Search | Print |
|---|---|---|
| Trie | O(L) | O(total chars) |
| BST (unbalanced) | O(L * log n) average, O(L * n) worst | O(n) |
| Dict | O(L) average | O(n log n) (sorting) |

## Running
    python index_generator.py input.txt output.txt          # default: dict
    python index_generator.py input.txt output.txt trie     # or bst / dict
    python benchmark.py --quick                              # fast test
    python benchmark.py                                      # full 6 files (needs RAM, takes a while)
