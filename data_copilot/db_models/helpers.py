from sqlalchemy.ext.compiler import compiles
from sqlalchemy import UUID


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(element, compiler, **kw):
    return "BLOB"
