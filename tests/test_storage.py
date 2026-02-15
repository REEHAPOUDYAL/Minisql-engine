import os
import tempfile
from minisql.storage.record_manager import RecordManager


def test_insert_and_select_records():
    with tempfile.TemporaryDirectory() as tmpdir:
        rm = RecordManager(base_path=tmpdir)

        rm.insert("users", {"id": "1", "name": "Alice", "age": "25"})
        rm.insert("users", {"id": "2", "name": "Bob", "age": "30"})

        records = rm.select_all("users")

        assert len(records) == 2
        assert records[0]["name"] == "Alice"
        assert records[1]["name"] == "Bob"


def test_delete_records():
    with tempfile.TemporaryDirectory() as tmpdir:
        rm = RecordManager(base_path=tmpdir)

        rm.insert("users", {"id": "1", "name": "Alice"})
        rm.insert("users", {"id": "2", "name": "Bob"})

        deleted = rm.delete_where("users", lambda r: r["id"] == "1")
        records = rm.select_all("users")

        assert deleted == 1
        assert len(records) == 1
        assert records[0]["id"] == "2"
