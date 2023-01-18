#!/usr/bin/env python3

from typing import NamedTuple


class Point(NamedTuple):
    x: int = 0
    y: int = 1
    z: int = 3

    def copy_with_updates(self, **kwargs):
        new_kwargs = self._asdict()
        new_kwargs.update(kwargs)
        return Point(**new_kwargs)


p = Point()
print(p)

q = p.copy_with_updates(z=5)
print(q)
