from pathlib import Path
from typing import Union
from minisql.utils.exceptions import FileManagerError
from minisql.config.settings import DEFAULT_ENCODING, DEFAULT_FILE_MODE, BUFFER_SIZE

class FileManager:
    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def read_file(self, filename: str, mode: str = DEFAULT_FILE_MODE) -> bytes:
        path = self.base_dir / filename
        if not path.exists():
            raise FileManagerError(f"File not found: {filename}")
        try:
            with open(path, mode) as f:
                return f.read()
        except Exception as e:
            raise FileManagerError(f"Failed to read file {filename}: {e}")

    def write_file(self, filename: str, data: bytes, mode: str = "wb") -> None:
        path = self.base_dir / filename
        try:
            with open(path, mode) as f:
                f.write(data)
        except Exception as e:
            raise FileManagerError(f"Failed to write file {filename}: {e}")

    def append_file(self, filename: str, data: bytes) -> None:
        self.write_file(filename, data, mode="ab")

    def exists(self, filename: str) -> bool:
        return (self.base_dir / filename).exists()

    def delete_file(self, filename: str) -> None:
        path = self.base_dir / filename
        if path.exists():
            try:
                path.unlink()
            except Exception as e:
                raise FileManagerError(f"Failed to delete file {filename}: {e}")

    def list_files(self) -> list[str]:
        return [f.name for f in self.base_dir.iterdir() if f.is_file()]
