from __future__ import annotations

import argparse
from pathlib import Path

from cortex.cli.commands import docstring as cmd_docstring
from cortex.cli.main_e3 import main


API_DOC = """
$0
GTYP:attrs{name:"attrs",desc:"key:value pairs"}
GTYP:cuerpo{name:"cuerpo",desc:"literal text body"}
GSIG:IDN{name:"identity",type:"attrs",risk:"B",layer:"Semantic",desc:"command identity"}
GSIG:DESC{name:"description",type:"cuerpo",risk:"B",layer:"Semantic",desc:"description"}
GSIG:ARG{name:"argument",type:"attrs",risk:"B",layer:"Semantic",desc:"argument"}
$1
IDN:command{name:"canonicalize",cli:"cortex canonicalize",status:"current",requires:"cortex 0.3.2+"}
DESC:summary{Normaliza artefactos CORTEX sin cambiar su semántica.}
ARG:input{name:"input",required:"yes",description:"Archivo fuente"}
ARG:out{name:"--out",required:"no",description:"Archivo destino"}
"""


def test_parse_and_render_docstring(tmp_path: Path):
    source = tmp_path / "canonicalize.cortex"
    source.write_text(API_DOC, encoding="utf-8")
    rendered = cmd_docstring.render_docstring(cmd_docstring.parse_api_doc(source))
    assert "Perfil: HCORTEX-REF" in rendered
    assert "`cortex canonicalize`" in rendered
    assert "`--out`" in rendered


def test_docstring_command_outputs_text(tmp_path: Path, capsys):
    docs_root = tmp_path / "docs" / "cortex" / "api"
    docs_root.mkdir(parents=True)
    (docs_root / "canonicalize.cortex").write_text(API_DOC, encoding="utf-8")
    args = argparse.Namespace(command="canonicalize", all=False, docs_root=str(docs_root), format="text")
    assert cmd_docstring.run(args) == 0
    assert "cortex canonicalize" in capsys.readouterr().out


def test_main_e3_routes_docstring(tmp_path: Path, capsys):
    docs_root = tmp_path / "docs" / "cortex" / "api"
    docs_root.mkdir(parents=True)
    (docs_root / "canonicalize.cortex").write_text(API_DOC, encoding="utf-8")
    rc = main(["docstring", "canonicalize", "--docs-root", str(docs_root)])
    assert rc == 0
    assert "cortex canonicalize" in capsys.readouterr().out
