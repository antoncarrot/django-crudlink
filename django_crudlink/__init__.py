from importlib.metadata import version

from .columns import ColumnMeta, column

__all__ = ("ColumnMeta", "column")
__version__ = version("django-crudlink")
