from abc import ABC, abstractmethod
from typing import Callable, Generic, Optional, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")
F = TypeVar("F")


class ResultException(Exception):
    pass


class AbstractResult(ABC, Generic[T, E]):
    @abstractmethod
    def is_ok(self) -> bool:
        pass

    @abstractmethod
    def is_err(self) -> bool:
        pass

    @abstractmethod
    def ok(self) -> Optional[T]:
        pass

    @abstractmethod
    def err(self) -> Optional[E]:
        pass

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Result[U, E]":
        pass

    @abstractmethod
    def map_err(self, f: Callable[[E], F]) -> "Result[T, F]":
        pass

    @abstractmethod
    def unwrap_or(self, val: T) -> T:
        pass

    @abstractmethod
    def unwrap(self) -> T:
        pass

    @abstractmethod
    def expect(self, msg: str) -> T:
        pass

    @abstractmethod
    def unwrap_err(self) -> E:
        pass

    @abstractmethod
    def expect_err(self, msg: str) -> E:
        pass


class Ok(AbstractResult, Generic[T]):
    def __init__(self, value: T):
        self._value = value

    def __repr__(self):
        return f"Ok({self._value})"

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def ok(self) -> Optional[T]:
        return self._value

    def err(self) -> Optional[E]:
        return None

    def map(self, f: Callable[[T], U]) -> "Result[U, E]":
        return Ok(f(self._value))

    def map_err(self, f: Callable[[E], F]) -> "Result[T, F]":
        return self

    def unwrap_or(self, val: T) -> T:
        return self._value

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> E:
        raise ResultException(f"{self._value}")

    def expect(self, msg: str) -> T:
        return self._value

    def expect_err(self, msg: str) -> E:
        raise ResultException(f"{msg}: {self._value}")


class Err(AbstractResult, Generic[E]):
    def __init__(self, err_value: E):
        self._err_value = err_value

    def __repr__(self):
        return f"Err({self._err_value})"

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def ok(self) -> Optional[T]:
        return None

    def err(self) -> Optional[E]:
        return self._err_value

    def map(self, f: Callable[[T], U]) -> "Result[U, E]":
        return self

    def map_err(self, f: Callable[[E], F]) -> "Result[T, F]":
        return Err(f(self._err_value))

    def unwrap_or(self, val: T) -> T:
        return val

    def unwrap(self) -> T:
        raise ResultException(f"{self._err_value}")

    def unwrap_err(self) -> E:
        return self._err_value

    def expect(self, msg: str) -> T:
        raise ResultException(f"{msg}: {self._err_value}")

    def expect_err(self, msg: str) -> E:
        return self._err_value


Result = Union[Ok[T], Err[E]]  # pylint: disable=unsubscriptable-object
