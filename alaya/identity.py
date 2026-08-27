"""本願 — the vow. What this agent is for, and what it will not do.

Yogācāra is a school of 瑜伽行 ("yoga practice"), and its practitioners are
瑜伽師 / yogācārin. Practice there is not decoration on the theory: 轉依,
the transformation of the basis, is the whole point of the analysis. An agent
built on this architecture needs an equivalent — something fixed that the
mutable layers are answerable to.

That is what identity is. Manas may revise the self-model freely; the store
records whatever happens; but ``hard_rules`` do not move, and they are the only
part of the prompt that no layer can rewrite.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Identity:
    name: str
    purpose: str
    hard_rules: tuple[str, ...]
    language: str = "English"

    @classmethod
    def load(cls, path: Path | str) -> "Identity":
        import yaml

        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls(
            name=data["name"],
            purpose=data["purpose"].strip(),
            hard_rules=tuple(data.get("hard_rules", ())),
            language=data.get("language", "English"),
        )
