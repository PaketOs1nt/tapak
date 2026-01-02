import abc
import difflib
import random
from functools import lru_cache
from typing import Callable


class BaseScorer[T](abc.ABC):
    @abc.abstractmethod
    def get_distance(self, a: T, b: T) -> float:
        return 1 if a != b else 0


class IntScorer(BaseScorer[int]):
    def get_distance(self, a: int, b: int) -> float:
        return max(a, b) - min(a, b)


class StrScorer(BaseScorer[str]):
    @staticmethod
    @lru_cache(maxsize=100000)
    def _get_distance(a: str, b: str) -> float:
        return 1 - difflib.SequenceMatcher(None, a, b).ratio()

    def get_distance(self, a: str, b: str) -> float:
        return self._get_distance(a, b)


class Model[T]:
    def __init__(self, n: int) -> None:
        self.data: dict[tuple[T, ...], list[T]] = {}
        self.scorer: BaseScorer[T] | None = None
        self.n: int = n

    def predict(self, data: tuple[T, ...]) -> T | None:
        if data in self.data:
            return random.choice(self.data[data])

    def learn(self, data: list[T]):
        pointer = 0
        while pointer < len(data) - self.n:
            K = tuple(data[pointer : pointer + self.n])
            V = data[pointer + self.n]

            if K not in self.data:
                self.data[K] = [V]
            else:
                self.data[K].append(V)

            pointer += 1

    def smart_predict(self, data: tuple[T, ...]) -> T | None:
        assert self.scorer is not None
        assert len(data) == self.n

        if data in self.data:
            return self.predict(data)

        min_score = float("inf")
        result = None

        for K, V in self.data.items():
            score = 0
            for a, b in zip(K, data):
                score += self.scorer.get_distance(a, b)
                if score >= min_score:
                    break

            if score < min_score:
                result = random.choice(V)
                min_score = score

        return result

    def sequence(
        self,
        data: tuple[T, ...],
        lenth: int,
        stop_token: T | None = None,
        on_token: Callable[[T], None] = lambda x: None,
    ) -> tuple[T, ...]:
        current = data
        final = []
        for _ in range(lenth):
            result = self.smart_predict(current)
            if result is None or (result == stop_token and stop_token is not None):
                break

            current = current[1 : len(current)] + (result,)
            on_token(result)

            final.append(result)
        return tuple(final)
