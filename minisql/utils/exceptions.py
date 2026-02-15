class MiniSQLError(Exception):
    pass

class SchemaError(MiniSQLError):
    pass

class TableNotFoundError(MiniSQLError):
    pass

class ColumnNotFoundError(MiniSQLError):
    pass

class RecordNotFoundError(MiniSQLError):
    pass

class DuplicateRecordError(MiniSQLError):
    pass

class SerializationError(MiniSQLError):
    pass

class FileManagerError(MiniSQLError):
    pass

class QueryParseError(MiniSQLError):
    pass

class IndexError(MiniSQLError):
    pass
