"""
index_generator.py  -  Index Generation utility (Chanakya University, Lab Exam 2)

Usage:
    python index_generator.py <input_file> <output_file> [trie|bst|dict]

Reads a text file, finds every word, and writes an index:
    word: line1, line2, line3
with the words in lexicographic (ASCII) order.

Three implementations of the index are given:
    1. TrieIndex  - Trie (character tree)
    2. BSTIndex   - Binary Search Tree
    3. DictIndex  - Python dictionary
All three have the SAME three methods, so they are easy to swap/extend:
    add(word, line_no)   -> insert a word occurrence
    search(word)         -> return list of line numbers (or None)
    write(out_file)      -> print the index in sorted order to a file
"""
import re
import sys

# Words are separated by: blanks, (tabs), full stop, comma, colon, semicolon.
# Line breaks are handled because we read the file line by line.
SEPARATORS = re.compile(r"[ \t.,:;]+")


def split_words(line):
    """Split one line into words (ignores empty pieces)."""
    return [w for w in SEPARATORS.split(line.rstrip("\r\n")) if w != ""]


# ---------------------------------------------------------------------------
# Linked-list queue that stores the line numbers of a word
# ---------------------------------------------------------------------------
class LineNode:
    """One node of the linked list: holds a line number."""
    __slots__ = ("line_no", "next")

    def __init__(self, line_no):
        self.line_no = line_no
        self.next = None


class LineQueue:
    """Queue (FIFO) of line numbers using a singly linked list.
    We keep both head and tail, so adding at the end is O(1)."""
    __slots__ = ("head", "tail")

    def __init__(self):
        self.head = None
        self.tail = None

    def enqueue(self, line_no):
        # If the word appears twice on the same line, store the line only once.
        if self.tail is not None and self.tail.line_no == line_no:
            return
        node = LineNode(line_no)
        if self.head is None:          # empty queue
            self.head = self.tail = node
        else:                          # attach at the end
            self.tail.next = node
            self.tail = node

    def to_list(self):
        """Walk the linked list and return the line numbers as a Python list."""
        result = []
        cur = self.head
        while cur is not None:
            result.append(cur.line_no)
            cur = cur.next
        return result


def format_entry(word, queue):
    """One output line:  word: 1, 4, 9"""
    return word + ": " + ", ".join(str(n) for n in queue.to_list()) + "\n"


# ---------------------------------------------------------------------------
# 1) TRIE
# ---------------------------------------------------------------------------
class TrieNode:
    __slots__ = ("children", "lines")

    def __init__(self):
        self.children = {}     # character -> TrieNode
        self.lines = None      # LineQueue; not None only if a word ends here


class TrieIndex:
    def __init__(self):
        self.root = TrieNode()

    def add(self, word, line_no):
        node = self.root
        for ch in word:                       # walk/create one node per character
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        if node.lines is None:                # first time this word is seen
            node.lines = LineQueue()
        node.lines.enqueue(line_no)

    def search(self, word):
        node = self.root
        for ch in word:
            node = node.children.get(ch)
            if node is None:
                return None
        return node.lines.to_list() if node.lines is not None else None

    def write(self, out_file):
        # Depth-first walk visiting children in sorted (ASCII) order gives
        # lexicographic order (a word comes before longer words it prefixes).
        with open(out_file, "w") as f:
            self._walk(self.root, [], f)

    def _walk(self, node, prefix, f):
        if node.lines is not None:            # a complete word ends here
            f.write(format_entry("".join(prefix), node.lines))
        for ch in sorted(node.children):
            prefix.append(ch)
            self._walk(node.children[ch], prefix, f)
            prefix.pop()


# ---------------------------------------------------------------------------
# 2) BINARY SEARCH TREE (not balanced)
# ---------------------------------------------------------------------------
class BSTNode:
    __slots__ = ("word", "lines", "left", "right")

    def __init__(self, word):
        self.word = word
        self.lines = LineQueue()
        self.left = None
        self.right = None


class BSTIndex:
    def __init__(self):
        self.root = None

    def add(self, word, line_no):
        # Iterative insert (no recursion -> no recursion-depth problems).
        if self.root is None:
            self.root = BSTNode(word)
            self.root.lines.enqueue(line_no)
            return
        cur = self.root
        while True:
            if word == cur.word:              # repeated word: just add line no.
                cur.lines.enqueue(line_no)
                return
            elif word < cur.word:             # Python compares strings by ASCII
                if cur.left is None:
                    cur.left = BSTNode(word)
                    cur.left.lines.enqueue(line_no)
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = BSTNode(word)
                    cur.right.lines.enqueue(line_no)
                    return
                cur = cur.right

    def search(self, word):
        cur = self.root
        while cur is not None:
            if word == cur.word:
                return cur.lines.to_list()
            cur = cur.left if word < cur.word else cur.right
        return None

    def write(self, out_file):
        # Iterative in-order traversal (left, node, right) = sorted order.
        with open(out_file, "w") as f:
            stack = []
            cur = self.root
            while stack or cur is not None:
                while cur is not None:
                    stack.append(cur)
                    cur = cur.left
                cur = stack.pop()
                f.write(format_entry(cur.word, cur.lines))
                cur = cur.right


# ---------------------------------------------------------------------------
# 3) PYTHON DICTIONARY
# ---------------------------------------------------------------------------
class DictIndex:
    def __init__(self):
        self.table = {}                       # word -> LineQueue

    def add(self, word, line_no):
        if word not in self.table:
            self.table[word] = LineQueue()
        self.table[word].enqueue(line_no)

    def search(self, word):
        q = self.table.get(word)
        return q.to_list() if q is not None else None

    def write(self, out_file):
        # A dict has no order, so we sort the keys before printing.
        with open(out_file, "w") as f:
            for word in sorted(self.table):
                f.write(format_entry(word, self.table[word]))


# ---------------------------------------------------------------------------
# Building an index from a file / main program
# ---------------------------------------------------------------------------
METHODS = {"trie": TrieIndex, "bst": BSTIndex, "dict": DictIndex}


def build_index(lines, method):
    """Create an index of the chosen type from a list of text lines."""
    index = METHODS[method]()
    for line_no, line in enumerate(lines, start=1):   # line numbers start at 1
        for word in split_words(line):
            index.add(word, line_no)
    return index


def read_lines(path):
    with open(path, "r", encoding="ascii", errors="replace") as f:
        return f.readlines()


def main():
    if len(sys.argv) < 3:
        print("Usage: python index_generator.py <input_file> <output_file> [trie|bst|dict]")
        sys.exit(1)
    in_file, out_file = sys.argv[1], sys.argv[2]
    method = sys.argv[3] if len(sys.argv) > 3 else "dict"   # default: dictionary
    if method not in METHODS:
        print("Method must be one of: trie, bst, dict")
        sys.exit(1)

    index = build_index(read_lines(in_file), method)
    index.write(out_file)
    print(f"Index written to {out_file} using {method}")


if __name__ == "__main__":
    main()
