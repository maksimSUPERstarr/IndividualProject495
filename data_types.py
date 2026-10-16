"""Обозначения типов коллекций ПР2; классы появятся в ПР3."""

from typing import Any

Record = dict[str, Any]
Records = list[Record]
AppData = dict[str, Records]
