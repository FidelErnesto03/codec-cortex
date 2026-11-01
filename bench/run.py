"""BLP-003 — Orquestador de sub-agentes (conexion nativa cmd).

Este modulo NO contiene claves de API ni llamadas HTTP. Los "adaptadores de
modelo" son lanzamientos de sub-agentes con el modelo fijado al arrancar, hechos
por la sesion de Alfred via la herramienta `agent`. Aqui solo dejamos el
contrato de datos que la sesion debe materializar en bench/results/run-<id>/raw/.

Los sub-agentes son de un solo nivel (profundidad 1): no lanzan sub-agentes.
La orquestacion vive exclusivamente en la sesion de Alfred.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

BENCH = Path(__file__).resolve().parent
RESULTS = BENCH / "results"


@dataclass
class Cell:
    """Una celda del diseno: un (modelo, formato, pregunta, repeticion)."""

    model: str
    fmt: str
    question: str
    rep: int
    output: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "format": self.fmt,
            "question": self.question,
            "rep": self.rep,
            "output": self.output,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost_usd": round(self.cost_usd, 6),
            "error": self.error,
        }


@dataclass
class Run:
    run_id: str = field(default_factory=lambda: time.strftime("run-%Y%m%dT%H%M%SZ", time.gmtime()))
    preregistration: str = ""
    cells: list[Cell] = field(default_factory=list)

    def add(self, cell: Cell) -> Cell:
        self.cells.append(cell)
        return cell

    def save(self) -> Path:
        outdir = RESULTS / self.run_id
        raw = outdir / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        (raw / "cells.json").write_text(
            json.dumps([c.to_dict() for c in self.cells], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (outdir / "run.json").write_text(
            json.dumps({"run_id": self.run_id, "preregistration": self.preregistration, "cells": len(self.cells)},
                       indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return outdir


def load_models() -> list[dict]:
    """Lee bench/models.yaml (ids exactos + tarifas)."""
    import re

    text = (BENCH / "models.yaml").read_text(encoding="utf-8")
    models = []
    for block in re.split(r"\n  - id:", text)[1:]:
        block = "  - id:" + block
        mid = re.search(r"id:\s*(\S+)", block).group(1)
        pin = re.search(r"price_in_usd_1m:\s*([\d.]+)", block)
        pout = re.search(r"price_out_usd_1m:\s*([\d.]+)", block)
        role = re.search(r"role:\s*(\S+)", block)
        models.append({
            "id": mid,
            "price_in_usd_1m": float(pin.group(1)) if pin else 0.0,
            "price_out_usd_1m": float(pout.group(1)) if pout else 0.0,
            "role": role.group(1) if role else "modelo",
        })
    return models


def cost_usd(tokens_in: int, tokens_out: int, model: dict) -> float:
    return (tokens_in * model["price_in_usd_1m"] + tokens_out * model["price_out_usd_1m"]) / 1_000_000