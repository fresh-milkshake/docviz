from typing import TypeAlias

numeric: TypeAlias = int | float
"""A number that can be either an integer or a float."""

RectangleTuple: TypeAlias = tuple[numeric, numeric, numeric, numeric]
"""A rectangle defined by (x1, y1, x2, y2) coordinates."""

RectangleList: TypeAlias = list[float]
"""A list of rectangles defined by (x1, y1, x2, y2) coordinates."""

RectangleUnion: TypeAlias = RectangleTuple | RectangleList
"""A rectangle defined by (x1, y1, x2, y2) coordinates or a list of rectangles."""

Color: TypeAlias = tuple[int, int, int]
"""An RGB color represented as a tuple (R, G, B)."""
