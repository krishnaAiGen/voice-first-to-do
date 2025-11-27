"""CRUD operations using Strategy pattern"""

from app.operations.base_operation import BaseOperation
from app.operations.create_operation import CreateOperation
from app.operations.read_operation import ReadOperation
from app.operations.update_operation import UpdateOperation
from app.operations.delete_operation import DeleteOperation

__all__ = [
    "BaseOperation",
    "CreateOperation",
    "ReadOperation",
    "UpdateOperation",
    "DeleteOperation"
]

