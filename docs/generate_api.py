from pathlib import Path

import pydpeet

GROUPS = {
    "Read and write": {
        "description": (
            "Functions for reading, converting, and exporting battery test data " "in the unified PyDPEET format."
        ),
        "items": [],
    },
    "Sequence and primitive processing": {
        "description": (
            "Functions for detecting, correcting, filtering, and visualizing " "test sequences and primitive segments."
        ),
        "items": [],
    },
    "Add derived quantities": {
        "description": (
            "Functions that add derived quantities such as SOC, capacity, " "or resistance to existing datasets."
        ),
        "items": [],
    },
    "Extract data": {
        "description": (
            "Functions for extracting OCV points, sequence summaries, "
            "and other reduced representations from datasets."
        ),
        "items": [],
    },
    "Citation utilities": {
        "description": ("Utilities for handling references, citations, and BibTeX export."),
        "items": [],
    },
    "Other": {
        "description": (
            "Additional public functions, classes, configurations, and utilities "
            "that do not belong to one of the main API categories."
        ),
        "items": [],
    },
}


def group_api_items(names: list[str]) -> dict[str, dict[str, list[str] | str]]:
    """Group public API names into documentation sections."""
    groups = {
        title: {
            "description": group["description"],
            "items": [],
        }
        for title, group in GROUPS.items()
    }

    for name in names:
        name_lower = name.lower()

        if name_lower in {"read", "write", "convert", "merge_into_series"}:
            groups["Read and write"]["items"].append(name)

        elif (
            "sequence" in name_lower
            or "primitive" in name_lower
            or name_lower
            in {
                "visualize_phases",
                "generate_instructions",
                "filter_and_split_df_by_blocks",
            }
        ):
            groups["Sequence and primitive processing"]["items"].append(name)

        elif name_lower.startswith("add_"):
            groups["Add derived quantities"]["items"].append(name)

        elif name_lower.startswith("extract_"):
            groups["Extract data"]["items"].append(name)

        elif "cite" in name_lower or "citation" in name_lower or "reference" in name_lower or "bibtex" in name_lower:
            groups["Citation utilities"]["items"].append(name)

        else:
            groups["Other"]["items"].append(name)

    return groups


def autosummary_block(names: list[str], title: str) -> str:
    """Create an autosummary block for a list of public API names."""
    items = "\n".join(f"   pydpeet.{name}" for name in sorted(names))

    return (
        "```{eval-rst}\n"
        ".. autosummary::\n"
        # "   :toctree: ../_autosummary\n"
        "   :nosignatures:\n\n"
        f"   :caption: {title}\n"
        f"{items}\n"
        "```\n"
    )


def toctree_block(names: list[str], title: str) -> str:
    items = "\n".join(f"../_autosummary/pydpeet.{name}" for name in sorted(names))
    return "```{toctree}\n" ":maxdepth: 2\n" f":caption: {title}\n" ":hidden:\n\n" f"{items}\n" "```\n"


def generate_api() -> None:
    """Generate API reference page."""
    docs_dir = Path(__file__).resolve().parent
    out = docs_dir / "api" / "index.md"

    names = list(pydpeet.__all__)
    groups = group_api_items(names)

    content = (
        "# API Reference\n\n"
        "This page documents the public top-level PyDPEET API.\n\n"
        "The functions are grouped according to a typical PyDPEET workflow:\n\n"
        "1. Read and write battery test data\n"
        "2. Process and structure sequences and primitive segments\n"
        "3. Add derived quantities such as SOC, capacity, or resistance\n"
        "4. Extract reduced representations and analysis data\n\n"
        "Additional utilities and citation helpers are listed separately.\n\n"
    )

    for title, group in groups.items():
        items = group["items"]

        if not items:
            continue

        content += f"## {title}\n\n"
        content += f"{group['description']}\n\n"
        content += autosummary_block(items, title)
        content += "\n"
        content += toctree_block(items, title)
        content += "\n"

    out.write_text(content, encoding="utf-8")
    print(f"Generated API reference at {out}")


if __name__ == "__main__":
    generate_api()
