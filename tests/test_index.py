from minisql.index.bplustree import BPlusTree


def test_bplustree_insert_and_search():
    tree = BPlusTree(order=4)

    tree.insert(10, "row10")
    tree.insert(20, "row20")
    tree.insert(5, "row5")

    assert tree.search(10) == "row10"
    assert tree.search(20) == "row20"
    assert tree.search(5) == "row5"
    assert tree.search(99) is None


def test_bplustree_multiple_inserts():
    tree = BPlusTree(order=4)

    for i in range(1, 50):
        tree.insert(i, f"row{i}")

    assert tree.search(1) == "row1"
    assert tree.search(25) == "row25"
    assert tree.search(49) == "row49"
