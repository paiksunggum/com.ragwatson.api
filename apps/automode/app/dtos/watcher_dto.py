from dataclasses import dataclass


@dataclass(frozen=True)
class WatcherQuery:
    id: int
    name: str


@dataclass(frozen=True)
class WatcherResponse:
    id: int
    name: str
