"""CLI helper for physical density-matrix PPT analysis."""
import json
import os
import sys

from agents.base import safe_resolve_path
from .ppt import analyze_density_matrix


def run_ppt_file(path: str) -> int:
    try:
        resolved = safe_resolve_path(path, must_exist=True)
        if os.stat(resolved).st_size > 1_000_000:
            raise ValueError("Density matrix input file must not exceed 1 MB")
        with open(resolved, encoding="utf-8") as stream:
            document = json.load(stream)
        if not isinstance(document, dict) or "matrix" not in document:
            raise ValueError("JSON input must contain a 'matrix' field")
        result = analyze_density_matrix(
            document["matrix"], document.get("dimensions", [2, 2])
        )
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"PPT analysis failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0
