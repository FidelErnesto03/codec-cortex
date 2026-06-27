"""``cortex add`` (alias: ``cortex patch_add``) — add a new entry to a .cortex file.

v1.1.2: post-mutation validation via :func:`~cortex.cli.commands.post_mutation_gate`.
v1.1.4 P0-3: ``--unsafe-allow-secret-forensics`` now marks the artefact as
``non_conformant_forensic_artifact`` via a ``STAT:forensic_quarantine`` entry,
so the file is explicitly flagged even though it's written.
"""

from __future__ import annotations

import json

from ...core.errors import CortexError
from ...core.parser import build_entry_from_value
from ...crud.mutations import add_entry
from ...crud.transactions import atomic_write_cortex
from ..commands import load_doc, post_mutation_gate


def run(args) -> int:
    doc = load_doc(args.input)
    try:
        entry = add_entry(
            doc,
            section=args.section,
            sigil=args.sigil,
            name=args.name,
            value=args.value,
            create_section=args.create_section,
            allow_duplicate=args.allow_duplicate,
            allow_unknown_sigil=getattr(args, "allow_unknown_sigil", False),
        )
    except CortexError as e:
        print(f"error: {e}")
        return 1

    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "dry_run": True,
            "entry": entry.to_dict(),
        }, indent=2, default=str))
        return 0

    # Post-mutation validation gate (shared with update/delete/move).
    err = post_mutation_gate(doc, args)
    if err is not None:
        print(json.dumps(err, indent=2, default=str))
        return 1

    # v1.1.4 P0-3: if --unsafe-allow-secret-forensics was used, mark the
    # artefact as non_conformant_forensic_artifact before writing.
    unsafe = getattr(args, "unsafe_allow_secret_forensics", False)
    if unsafe:
        # Ensure STAT is declared in $0
        if "STAT" not in doc.glossary.sigils:
            from ...glossary.minimal import brain_sigils
            canonical = {sd.sigil: sd for sd in brain_sigils()}
            if "STAT" in canonical:
                doc.glossary.add_sigil(canonical["STAT"])
        # Add forensic quarantine marker
        stat_sec = doc.get_or_create_section("$9", title="FORENSIC QUARANTINE")
        stat_sec.entries.append(build_entry_from_value(
            "$9", "STAT", "forensic_quarantine", "attrs",
            {
                "conformity": "non_conformant_forensic_artifact",
                "reason": "contains clear-text secret persisted via --unsafe-allow-secret-forensics",
                "status": "deprecated",
                "survive": "min",
            },
        ))

    result = atomic_write_cortex(
        doc, args.input, force=args.force,
        unsafe_allow_secret_forensics=unsafe,
    )

    payload = {
        "ok": True,
        "entry": entry.to_dict(),
        "written": result.to_dict(),
    }
    if unsafe:
        payload["warning"] = (
            "ARTEFACT MARKED AS non_conformant_forensic_artifact — "
            "contains clear-text secret; do NOT use as operational memory"
        )
    print(json.dumps(payload, indent=2, default=str))
    return 0
