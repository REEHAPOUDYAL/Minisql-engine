from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class BPlusNode:
    is_leaf: bool
    keys: list[Any] = field(default_factory=list)
    children: list[Any] = field(default_factory=list)
    next: Optional["BPlusNode"] = None


class BPlusTree:
    def __init__(self, order: int = 4):
        if order < 3:
            raise ValueError("Order must be >= 3")
        self.order = order
        self.root = BPlusNode(is_leaf=True)

    def search(self, key: Any):
        node = self.root
        while not node.is_leaf:
            idx = self._find_index(node.keys, key)
            node = node.children[idx]
        for i, k in enumerate(node.keys):
            if k == key:
                return node.children[i]
        return None

    def insert(self, key: Any, value: Any):
        root = self.root
        if len(root.keys) >= self.order - 1:
            new_root = BPlusNode(is_leaf=False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node: BPlusNode, key: Any, value: Any):
        if node.is_leaf:
            idx = self._find_index(node.keys, key)
            if idx < len(node.keys) and node.keys[idx] == key:
                node.children[idx] = value
                return
            node.keys.insert(idx, key)
            node.children.insert(idx, value)
            return

        idx = self._find_index(node.keys, key)
        child = node.children[idx]

        if len(child.keys) >= self.order - 1:
            self._split_child(node, idx)
            if key >= node.keys[idx]:
                idx += 1

        self._insert_non_full(node.children[idx], key, value)

    def _split_child(self, parent: BPlusNode, index: int):
        child = parent.children[index]
        mid = (self.order - 1) // 2

        if child.is_leaf:
            new_leaf = BPlusNode(is_leaf=True)
            new_leaf.keys = child.keys[mid:]
            new_leaf.children = child.children[mid:]
            child.keys = child.keys[:mid]
            child.children = child.children[:mid]

            new_leaf.next = child.next
            child.next = new_leaf

            parent.keys.insert(index, new_leaf.keys[0])
            parent.children.insert(index + 1, new_leaf)
        else:
            new_internal = BPlusNode(is_leaf=False)

            promote_key = child.keys[mid]

            new_internal.keys = child.keys[mid + 1:]
            new_internal.children = child.children[mid + 1:]

            child.keys = child.keys[:mid]
            child.children = child.children[:mid + 1]

            parent.keys.insert(index, promote_key)
            parent.children.insert(index + 1, new_internal)

    def _find_index(self, keys: list[Any], key: Any) -> int:
        lo, hi = 0, len(keys)
        while lo < hi:
            mid = (lo + hi) // 2
            if key < keys[mid]:
                hi = mid
            else:
                lo = mid + 1
        return lo
