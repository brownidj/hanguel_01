from __future__ import annotations

from typing import TypeVar, cast

from PyQt6.QtWidgets import QWidget

T = TypeVar("T", bound=QWidget)


def require_child(parent: QWidget, cls: type[T], object_name: str) -> T:
    """Find a named Qt child and raise a clear error if missing."""
    widget = parent.findChild(cls, object_name)
    if widget is None:
        raise RuntimeError(f"{object_name} not found (expected {cls.__name__})")
    return widget


def find_child(parent: QWidget, cls: type[T], object_name: str) -> T | None:
    """Typed wrapper around Qt's findChild() to keep IDE type inference precise."""
    return cast(T | None, parent.findChild(cls, object_name))


def find_children(parent: QWidget, cls: type[T]) -> list[T]:
    """Typed wrapper around Qt's findChildren() to keep IDE type inference precise."""
    return cast(list[T], parent.findChildren(cls))
