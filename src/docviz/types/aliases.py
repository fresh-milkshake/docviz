from typing import List, Tuple, TypeAlias, Union

numeric: TypeAlias = Union[int, float]
"""A number that can be either an integer or a float."""

RectangleTuple: TypeAlias = Tuple[numeric, numeric, numeric, numeric]
"""A rectangle defined by (x1, y1, x2, y2) coordinates."""

RectangleList: TypeAlias = List[float]
"""A list of rectangles defined by (x1, y1, x2, y2) coordinates."""

RectangleUnion: TypeAlias = Union[RectangleTuple, RectangleList]
"""A rectangle defined by (x1, y1, x2, y2) coordinates or a list of rectangles."""

Color: TypeAlias = Tuple[int, int, int]
"""An RGB color represented as a tuple (R, G, B)."""
