from typing import Callable, Dict, Iterable, List, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def group_by(func: Callable[[T], K], iterable: Iterable[T]) -> Dict[K, List[T]]:
    entries: Dict[K, List[T]] = {}
    for e in iterable:
        key = func(e)
        if key in entries:
            entries[key].append(e)
        else:
            entries[key] = [e]

    return entries
