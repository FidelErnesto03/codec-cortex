"""HCORTEX package — READ renderer, EDIT renderer, EDIT parser, profiles, recovery."""

from .profiles import (
    Profile, PROFILES, DEFAULT_PROFILE,
    resolve_profile, classify_entry, classify_doc,
    filter_by_profile, sort_by_plevel, plevel_rank,
)
from .read_renderer import render_hcortex_read
from .edit_renderer import render_hcortex_edit
from .edit_parser import parse_hcortex_edit, parse_glossary_block
from .markdown_model import (
    HCORTEX_READ_HEADER, HCORTEX_EDIT_HEADER,
    EditHeader, is_hcortex_read, is_hcortex_edit,
)
from .recovery import (
    RecoveryResult, recover_cortex, strip_preamble,
    normalise_legacy_type_name, LEGACY_TYPE_ALIASES, LEGACY_COLUMN_ALIASES,
)

__all__ = [
    # Profiles and priority classifier
    "Profile", "PROFILES", "DEFAULT_PROFILE",
    "resolve_profile", "classify_entry", "classify_doc",
    "filter_by_profile", "sort_by_plevel", "plevel_rank",
    # Renderers
    "render_hcortex_read", "render_hcortex_edit",
    # Parser
    "parse_hcortex_edit", "parse_glossary_block",
    # Markdown model
    "HCORTEX_READ_HEADER", "HCORTEX_EDIT_HEADER",
    "EditHeader", "is_hcortex_read", "is_hcortex_edit",
    # Recovery
    "RecoveryResult", "recover_cortex", "strip_preamble",
    "normalise_legacy_type_name", "LEGACY_TYPE_ALIASES", "LEGACY_COLUMN_ALIASES",
]
