"""The model behind the sixth consciousness.

意識 is the deliberating layer — 分別 (discrimination), 計度 (reckoning). In this
implementation an LLM does that work, so a provider is just the adapter between
:class:`~alaya.mano.Mano` and whatever model is available. Nothing doctrinal
lives here; this file exists so that the doctrine-bearing parts do not have to
know about API shapes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Call:
    """One tool the model wants invoked."""

    name: str
    args: dict
    id: str = "call"


@dataclass(frozen=True)
class Response:
    text: str | None = None
    calls: list[Call] = field(default_factory=list)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    schema: dict


class Provider(ABC):
    name = "provider"

    #: Whether there is actually a language model behind this. The reflective
    #: transformations (平等性智 asking for a corrective, ModelExaminer judging
    #: implication) consult it before delegating judgement. A stub that answers
    #: anyway does not fail loudly — it writes filler into the self-model, which
    #: 恆審思量 then carries into every prompt afterwards.
    deliberative = True

    @abstractmethod
    def converse(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> Response:
        """One round. Return the tool calls the model wants, or text to finish."""
