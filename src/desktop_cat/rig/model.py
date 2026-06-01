from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RigPart:
    name: str
    file: Path
    parent: str | None
    pivot: tuple[float, float]
    position: tuple[float, float]
    z_index: int
    scale: float
    rotation_limit: tuple[float, float]


@dataclass(frozen=True)
class RigModel:
    name: str
    canvas_size: tuple[int, int]
    parts_root: Path
    parts: dict[str, RigPart]

    @classmethod
    def load(cls, path: str | Path) -> "RigModel":
        rig_path = Path(path)
        data: dict[str, Any] = json.loads(rig_path.read_text(encoding="utf-8"))
        parts_root = rig_path.parent
        parts: dict[str, RigPart] = {}

        for part_data in data["parts"]:
            name = part_data["name"]
            parts[name] = RigPart(
                name=name,
                file=parts_root / part_data["file"],
                parent=part_data.get("parent"),
                pivot=tuple(part_data["pivot"]),
                position=tuple(part_data["position"]),
                z_index=int(part_data["z_index"]),
                scale=float(part_data.get("scale", 1.0)),
                rotation_limit=tuple(part_data.get("rotation_limit", [-30, 30])),
            )

        return cls(
            name=data["name"],
            canvas_size=tuple(data.get("canvas_size", [512, 512])),
            parts_root=parts_root,
            parts=parts,
        )
