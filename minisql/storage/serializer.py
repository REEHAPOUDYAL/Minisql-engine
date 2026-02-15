import json
from typing import Any
from minisql.utils.exceptions import SerializationError
from minisql.config.settings import DEFAULT_ENCODING

class Serializer:
    @staticmethod
    def serialize(obj: Any) -> bytes:
        try:
            data = json.dumps(obj, ensure_ascii=False)
            return data.encode(DEFAULT_ENCODING)
        except Exception as e:
            raise SerializationError(f"Serialization failed: {e}")

    @staticmethod
    def deserialize(data: bytes) -> Any:
        try:
            text = data.decode(DEFAULT_ENCODING)
            return json.loads(text)
        except Exception as e:
            raise SerializationError(f"Deserialization failed: {e}")

    @staticmethod
    def serialize_to_file(obj: Any, file_path: str) -> None:
        try:
            with open(file_path, "wb") as f:
                f.write(Serializer.serialize(obj))
        except Exception as e:
            raise SerializationError(f"Failed to write to file {file_path}: {e}")

    @staticmethod
    def deserialize_from_file(file_path: str) -> Any:
        try:
            with open(file_path, "rb") as f:
                return Serializer.deserialize(f.read())
        except Exception as e:
            raise SerializationError(f"Failed to read from file {file_path}: {e}")
