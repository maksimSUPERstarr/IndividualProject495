"""Объекты предметной области, независимые от Django ORM."""

from .assignments import Assignment
from .catalog import Catalog
from .managers import Manager
from .projects import Project

__all__ = ["Assignment", "Catalog", "Manager", "Project"]
