#!/usr/bin/env python3

from typing import NamedTuple


class ManaBase(NamedTuple):
    green: int = 0
    total: int = 0


m = ManaBase(1, 1)

n = ManaBase(2, 0)

print(m < n)
