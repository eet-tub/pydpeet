import ast
import json
import os
import re
from collections.abc import Iterable
from pathlib import Path

import pandas as pd


def _load_config(config: str | Path | dict) -> dict:
    """Load config.json from a path or return a dict unchanged."""
    if isinstance(config, str | Path):
        with open(Path(config), encoding="utf-8") as fh:
            return json.load(fh)
    elif isinstance(config, dict):
        return config
    else:
        raise TypeError("config must be a file path or a dict")


def _find_project_root(start: Path | None = None) -> Path:
    """Find project root by walking up from start (or cwd) looking for common markers."""
    markers = {"pyproject.toml", "setup.py", "setup.cfg", "Pipfile", ".git"}
    p = (start or Path.cwd()).resolve()
    for parent in [p] + list(p.parents):
        for m in markers:
            if (parent / m).exists():
                return parent
    return Path.cwd().resolve()


def _resolve_path_with_base(pathish: str | Path, base_dir: Path | None) -> Path:
    """Resolve a path-like value to an absolute Path."""
    p = Path(pathish)
    if p.is_absolute():
        return p.resolve()
    if base_dir is not None:
        return (base_dir / p).resolve()
    return (Path.cwd() / p).resolve()


def _resolve_config_base(config: str | Path | dict) -> Path:
    """Determine the base directory for resolving relative paths from the config."""
    if isinstance(config, str | Path):
        cfg_path = Path(config)
        if not cfg_path.is_absolute():
            cfg_path = _resolve_path_with_base(cfg_path, _find_project_root())
        return cfg_path.resolve().parent if cfg_path.exists() else _find_project_root()
    return _find_project_root()


def _sanitize_identifier(s: str) -> str:
    """Make a string safe for use as a Python identifier."""
    return re.sub(r"[^0-9a-zA-Z_]", "_", s)


def _get_args(args_obj: ast.arguments) -> list[str]:
    """Extract argument names from an ast.arguments node, skipping self/cls."""
    result = [a.arg for a in args_obj.args if a.arg not in ("self", "cls")]
    if args_obj.vararg and args_obj.vararg.arg not in ("self", "cls"):
        result.append(args_obj.vararg.arg)
    if args_obj.kwarg and args_obj.kwarg.arg not in ("self", "cls"):
        result.append(args_obj.kwarg.arg)
    return result


def _make_placeholder_class(class_name: str, param: str, export_name: str) -> str:
    """Return source text for a placeholder test class."""
    return (
        f"class {class_name}(object):\n"
        f'    """Placeholder failing test for variable \'{param}\' of \'{export_name}\'."""\n'
        f"    def test_placeholder(self):\n"
        f"        raise NotImplementedError('Test not implemented for variable: {param} of {export_name}')\n\n"
    )


def _class_name_for(export_name: str, param: str) -> str:
    """Build the canonical test-class name for a (export_name, param) pair."""
    return f"Test_{_sanitize_identifier(export_name)}_{_sanitize_identifier(param)}"


def _class_exists_in_source(source: str, class_name: str) -> bool:
    """Check whether a class with *class_name* exists at the top level of *source*."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(isinstance(n, ast.ClassDef) and n.name == class_name for n in tree.body)


def _collect_test_class_names_from_file(path: Path) -> set[str]:
    """Return the set of top-level class names defined in a test file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        return set()
    return {node.name for node in tree.body if isinstance(node, ast.ClassDef)}


def _find_deprecated_test_classes(
    test_dirs: list[Path],
    src_defs: dict[str, dict],
    exported_names: set[str],
    test_prefix: str,
    test_ext: str,
) -> set[str]:
    """Find test classes whose target name:param no longer exists in src_defs.

    Builds the set of *valid* test class names from src_defs, scans all test files
    for ``Test_*`` classes, and reports any that don't match a current source entity.
    """
    # All current source names (exported + everything found in src)
    all_src_names = set(src_defs.keys()) | exported_names

    # Build the set of valid test class names
    valid_classes: set[str] = set()
    for name in all_src_names:
        info = src_defs.get(name)
        if not info:
            continue
        for p in info.get("params", []):
            if p:
                valid_classes.add(_class_name_for(name, p))

    # Collect all Test_* class names from test files
    all_test_classes: dict[str, str] = {}  # class_name -> filename
    for test_dir in test_dirs:
        for py_file in _walk_py_files(test_dir, set(), test_ext):
            if not py_file.name.startswith(test_prefix):
                continue
            for cls_name in _collect_test_class_names_from_file(py_file):
                if cls_name.startswith("Test_"):
                    all_test_classes[cls_name] = py_file.name

    # Any Test_* class not in valid_classes is deprecated
    deprecated: set[str] = set()
    for cls_name, filename in sorted(all_test_classes.items()):
        if cls_name not in valid_classes:
            deprecated.add(f"{filename}::{cls_name}")
    return deprecated


def _collect_exported_names(cfg: dict) -> set[str]:
    """Collect the exported names from the config structure."""
    return {
        str(e)
        for details in cfg.values()
        if isinstance(details, dict)
        for e in (details.get("exports") or [])
        if isinstance(e, Iterable)
    }


# ---------------------------------------------------------------------------
# File / directory scanning
# ---------------------------------------------------------------------------


def _read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _walk_py_files(
    src_dir: Path,
    exclude_dirs: set[str],
    file_pattern: str = ".py",
) -> list[Path]:
    """Return resolved .py file paths under src_dir, pruning excluded dirs."""
    result: list[Path] = []
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith((".venv", "__pycache__"))]
        root_path = Path(root)
        for f in files:
            if f.endswith(file_pattern):
                result.append((root_path / f).resolve())
    return result


def _collect_defs_from_file(path: Path) -> dict[str, dict]:
    """Return mapping name -> {type, params, path} for top-level defs in a file."""
    try:
        src = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        return {}
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return {}

    result: dict[str, dict] = {}
    resolved = path.resolve()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            result[node.name] = {"type": "function", "params": _get_args(node.args), "path": resolved}
        elif isinstance(node, ast.ClassDef):
            init_args: list[str] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    init_args = _get_args(item.args)
                    break
            result[node.name] = {"type": "class", "params": init_args, "path": resolved}
    return result


def collect_defs_from_src(
    src_dir: str | Path = "src",
    exclude_dirs: Iterable[str] | None = None,
    file_pattern: str = ".py",
) -> tuple[dict[str, dict], dict[str, list[str]]]:
    """Walk src_dir and return (defs, duplicates).

    *defs* maps top-level name -> dict(type, params, path).
    When a name appears in multiple files the params are merged (union).

    *duplicates* maps name -> list of relative file paths where it is defined.
    Only names defined in 2+ files appear here.
    """
    _exclude = set(exclude_dirs or [])
    defs: dict[str, dict] = {}
    sources: dict[str, list[str]] = {}
    for full in _walk_py_files(Path(src_dir), _exclude, file_pattern):
        rel = str(full)
        for name, info in _collect_defs_from_file(full).items():
            sources.setdefault(name, []).append(rel)
            if name in defs:
                defs[name]["params"] = list(dict.fromkeys(defs[name]["params"] + info["params"]))
            else:
                defs[name] = info
    duplicates = {n: files for n, files in sources.items() if len(files) > 1}
    return defs, duplicates


# ---------------------------------------------------------------------------
# Test-file helpers
# ---------------------------------------------------------------------------


def _missing_files(
    expected: set[str],
    actual: set[str],
    case_sensitive: bool,
) -> tuple[set[str], set[str]]:
    """Return (missing, extra) file-name sets, with optional case-insensitive matching."""
    if case_sensitive:
        return expected - actual, actual - expected
    expected_lower = {s.lower(): s for s in expected}
    actual_lower = {s.lower(): s for s in actual}
    missing = {expected_lower[k] for k in expected_lower.keys() - actual_lower.keys()}
    extra = {actual_lower[k] for k in actual_lower.keys() - expected_lower.keys()}
    return missing, extra


def _list_test_files(directory: Path, prefix: str, ext: str) -> set[str]:
    """Return filenames in *directory* that match prefix and ext."""
    try:
        return {
            p.name for p in directory.iterdir() if p.is_file() and p.name.startswith(prefix) and p.name.endswith(ext)
        }
    except FileNotFoundError:
        return set()


def _ensure_dir_exists(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _append_failing_test_classes(
    test_file: Path,
    export_name: str,
    params: list[str],
    test_prefix: str = "test_",
) -> tuple[bool, list[str]]:
    """Append missing test classes for (export_name, params) to test_file."""
    _ensure_dir_exists(test_file.parent)
    text = _read_text_safe(test_file) if test_file.exists() else ""
    header_needed = text.strip() == ""
    added: list[str] = []

    for p in params:
        if not p:
            continue
        cls_name = _class_name_for(export_name, p)
        if _class_exists_in_source(text, cls_name):
            continue
        added.append(_make_placeholder_class(cls_name, p, export_name))

    if not added:
        return False, []

    if header_needed:
        text = "# Auto-generated test placeholders\n# Replace with real tests\n\n" + text
    text += "\n" + "".join(added)
    try:
        test_file.write_text(text, encoding="utf-8")
    except Exception:
        return False, []
    return True, [_class_name_for(export_name, p) for p in params if p]


def _create_placeholder_test_file(
    test_file: Path,
    export_name: str,
    params: list[str] | None = None,
) -> bool:
    """Create a new placeholder test file. Returns True if created."""
    _ensure_dir_exists(test_file.parent)
    if test_file.exists():
        return False
    header = "# Auto-generated test placeholder file\n# Fill in real tests and remove or adjust placeholders\n\n"
    body = "".join(
        _make_placeholder_class(_class_name_for(export_name, p), p, export_name) for p in (params or []) if p
    )
    try:
        test_file.write_text(header + body + "\n", encoding="utf-8")
        return True
    except Exception:
        return False


def _ensure_coverage_for_names(
    names: set[str],
    src_defs: dict[str, dict],
    tests_dir: Path,
    test_prefix: str,
    test_ext: str,
    case_sensitive: bool,
    auto_create: bool,
) -> tuple[set[str], set[str], set[str], dict]:
    """Ensure test coverage for a set of names. Returns (created_files, modified_files, missing_entries, summary)."""
    created_files: set[str] = set()
    modified_files: set[str] = set()
    missing_entries: set[str] = set()
    total_vars = covered_vars = 0

    actual_files = _list_test_files(tests_dir, test_prefix, test_ext)

    for name in names:
        expected_filename = f"{test_prefix}{name}{test_ext}"
        test_file_path = tests_dir / expected_filename
        info = src_defs.get(name)
        params: list[str] = info.get("params", []) if info else []

        # Auto-create missing test files (for names with no params or no file yet)
        if auto_create and expected_filename not in actual_files:
            if _create_placeholder_test_file(test_file_path, name, params=params):
                created_files.add(str(test_file_path.resolve()))
                actual_files.add(expected_filename)

        # Ensure test classes per input variable
        valid_params = [p for p in params if p]
        total_vars += len(valid_params)
        if not valid_params:
            continue

        existing_src = _read_text_safe(test_file_path)
        missing_for_file = [
            p for p in valid_params if not _class_exists_in_source(existing_src, _class_name_for(name, p))
        ]
        covered_vars += len(valid_params) - len(missing_for_file)
        missing_entries.update(f"{name}:{p}" for p in missing_for_file)

        if missing_for_file:
            changed, created_classes = _append_failing_test_classes(test_file_path, name, missing_for_file, test_prefix)
            if changed:
                target = modified_files if (existing_src and test_file_path.exists()) else created_files
                target.add(str(test_file_path.resolve()))
                covered_vars += len(created_classes)

    pct = round((covered_vars / total_vars * 100.0) if total_vars else 100.0, 2)
    summary = {"total_vars": total_vars, "covered_vars": covered_vars, "coverage_pct": pct}
    return created_files, modified_files, missing_entries, summary


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def _print_report(
    config: str | Path | dict,
    base_dir: Path,
    api_tests_dir: Path,
    private_tests_dir: Path,
    result: dict,
    phase: str = "all",
) -> None:
    counts = result["counts"]
    coverage = result["coverage"]

    if phase in ("header", "all"):
        print("=== test existence & private-coverage check ===")
        print(f"config.py: {config}")
        print(f"Base dir: {base_dir}")
        print(f"API Tests folder: {api_tests_dir.resolve()}")
        print(f"Private Tests folder: {private_tests_dir.resolve()}\n")

    if phase in ("before", "after", "all"):
        print(
            pd.DataFrame(
                [
                    {
                        "Group": "Exports",
                        "Total": counts["exports_total"],
                        "Covered": counts["exports_covered"],
                        "Missing": counts["exports_missing"],
                        "Coverage%": coverage["exports_pct"],
                    },
                    {
                        "Group": "Private",
                        "Total": counts["private_total"],
                        "Covered": counts["private_covered"],
                        "Missing": counts["private_missing"],
                        "Coverage%": coverage["private_pct"],
                    },
                    {
                        "Group": "Overall",
                        "Total": counts["overall_total"],
                        "Covered": counts["overall_covered"],
                        "Missing": counts["overall_total"] - counts["overall_covered"],
                        "Coverage%": coverage["overall_pct"],
                    },
                ]
            ).to_string(index=False)
        )

    if phase in ("changes", "all"):
        for label, items in [
            ("Missing export test files", result["exports_missing_files"]),
            ("Missing private test files", result["private_missing_test_files"]),
        ]:
            if items:
                print(f"\n{label} ({len(items)}):")
                for f in sorted(items):
                    print(f"  - {f}")

        extra = result["extra_test_files"]
        if extra:
            print(f"\nExtra test files ({len(extra)}) — may be deprecated, no matching export or private name found:")
            for f in sorted(extra):
                print(f"  - {f}")

        created = result["created_placeholder_files"]
        modified = result["modified_files"]
        if created or modified:
            print("\nPlaceholder changes:")
            for f in sorted(created):
                print(f"  [CREATED] {f}")
            for f in sorted(modified):
                print(f"  [MODIFIED] {f}")

        missing_var = result.get("missing_var_entries", set())
        if missing_var:
            print(f"\nMissing test classes for input variables ({len(missing_var)}):")
            for entry in sorted(missing_var):
                print(f"  - {entry}")

    if phase in ("after", "all"):
        deprecated = result.get("deprecated_test_classes", set())
        if deprecated:
            print(f"\nDeprecated test classes — target no longer exists in source ({len(deprecated)}):")
            for entry in sorted(deprecated):
                print(f"  - {entry}")

        duplicates = result.get("duplicate_names", {})
        if duplicates:
            print(f"\nDuplicate source names — defined in multiple files ({len(duplicates)}):")
            for name in sorted(duplicates):
                files = duplicates[name]
                print(f"  - {name} ({len(files)} definitions):")
                for f in files:
                    print(f"      {f}")

        for label, key in [
            ("exports", "input_variable_checks_exports"),
            ("private/internal", "input_variable_checks_private"),
        ]:
            summary = result.get(key, {})
            if summary and summary.get("total_vars"):
                print(
                    f"\nInput-variable coverage ({label}): {summary['covered_vars']}/{summary['total_vars']} ({summary['coverage_pct']}%)"
                )

    if phase == "all":
        print(f"\n{'='*47}")
        if counts["overall_covered"] < counts["overall_total"]:
            raise ValueError("Test coverage check failed")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def check_tests_and_generate_missing_test_files(
    config: str | Path | dict,
    tests_dir: str | Path | tuple[str | Path, str | Path] = "pydpeet/test/api_accessible",
    src_dir: str | Path = "src",
    exclude_dirs: Iterable[str] | None = None,
    test_prefix: str = "test_",
    test_ext: str = ".py",
    case_sensitive: bool = True,
    include_private: bool = True,
    auto_create_missing_input_var_tests: bool = True,
    auto_create_missing_test_files: bool = True,
    print_report: bool = True,
) -> dict[str, object]:
    """
    Check that every exported name from config has a corresponding test file,
    optionally scan for private names, and create placeholder tests when missing.
    """
    base_dir = _resolve_config_base(config)
    src_dir = _resolve_path_with_base(src_dir, base_dir)

    if isinstance(tests_dir, tuple):
        api_tests_dir = _resolve_path_with_base(tests_dir[0], base_dir)
        private_tests_dir = _resolve_path_with_base(tests_dir[1], base_dir)
    else:
        api_tests_dir = _resolve_path_with_base(tests_dir, base_dir)
        private_tests_dir = api_tests_dir

    cfg = _load_config(config)
    exported_names = _collect_exported_names(cfg)
    src_defs, duplicate_names = collect_defs_from_src(src_dir=src_dir, exclude_dirs=exclude_dirs)

    # --- Export coverage ---
    expected_export_files = {f"{test_prefix}{n}{test_ext}" for n in exported_names}
    actual_test_files = _list_test_files(api_tests_dir, test_prefix, test_ext)
    exports_missing_files, extra_test_files = _missing_files(expected_export_files, actual_test_files, case_sensitive)

    # --- Private coverage ---
    private_names_found: set[str] = set()
    private_missing_test_files: set[str] = set()
    private_total = 0

    if include_private:
        private_names_found = {n for n in src_defs if n.startswith("_") and n not in exported_names}
        expected_private_files = {f"{test_prefix}{n}{test_ext}" for n in private_names_found}
        actual_test_files_private = _list_test_files(private_tests_dir, test_prefix, test_ext)
        private_missing_test_files, _ = _missing_files(
            expected_private_files, actual_test_files_private, case_sensitive
        )
        private_total = len(expected_private_files)

    # --- Auto-create files + ensure test classes per variable ---
    created_placeholder_files: set[str] = set()
    modified_files: set[str] = set()
    missing_var_entries: set[str] = set()
    exports_summary: dict = {}
    private_summary: dict = {}

    if auto_create_missing_input_var_tests or auto_create_missing_test_files:
        cr, mo, mi, exports_summary = _ensure_coverage_for_names(
            exported_names,
            src_defs,
            api_tests_dir,
            test_prefix,
            test_ext,
            case_sensitive,
            auto_create_missing_test_files,
        )
        created_placeholder_files |= cr
        modified_files |= mo
        missing_var_entries |= mi

        if include_private:
            cr, mo, mi, private_summary = _ensure_coverage_for_names(
                private_names_found,
                src_defs,
                private_tests_dir,
                test_prefix,
                test_ext,
                case_sensitive,
                auto_create_missing_test_files,
            )
            created_placeholder_files |= cr
            modified_files |= mo
            missing_var_entries |= mi

    # --- Build summary ---
    export_total = len(expected_export_files)
    export_covered = export_total - len(exports_missing_files)
    private_covered = private_total - len(private_missing_test_files)
    overall_total = export_total + private_total
    overall_covered = export_covered + private_covered

    # --- Deprecated test classes ---
    test_dirs_list = [d for d in [api_tests_dir, private_tests_dir] if d != private_tests_dir or include_private]
    if not include_private:
        test_dirs_list = [api_tests_dir]
    deprecated_test_classes = _find_deprecated_test_classes(
        test_dirs_list, src_defs, exported_names, test_prefix, test_ext
    )

    result = {
        "exports_expected_files": expected_export_files,
        "exports_actual_files": actual_test_files,
        "exports_missing_files": exports_missing_files,
        "extra_test_files": extra_test_files,
        "private_names_found": private_names_found,
        "private_missing_test_files": private_missing_test_files,
        "counts": {
            "exports_total": export_total,
            "exports_covered": export_covered,
            "exports_missing": len(exports_missing_files),
            "private_total": private_total,
            "private_covered": private_covered,
            "private_missing": len(private_missing_test_files),
            "overall_total": overall_total,
            "overall_covered": overall_covered,
        },
        "coverage": {
            "exports_pct": round((export_covered / export_total * 100.0) if export_total else 100.0, 2),
            "private_pct": round((private_covered / private_total * 100.0) if private_total else 100.0, 2),
            "overall_pct": round((overall_covered / overall_total * 100.0) if overall_total else 100.0, 2),
        },
        "input_variable_checks_exports": exports_summary,
        "input_variable_checks_private": private_summary,
        "created_placeholder_files": created_placeholder_files,
        "modified_files": modified_files,
        "missing_var_entries": missing_var_entries,
        "deprecated_test_classes": deprecated_test_classes,
        "duplicate_names": duplicate_names,
    }

    if print_report:
        _print_report(config, base_dir, api_tests_dir, private_tests_dir, result, phase="all")
    return result
