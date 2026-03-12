import ast
import json
import os
import re
from collections.abc import Iterable
from pathlib import Path


def _load_config(config: str | Path | dict) -> dict:
    """Load config.json from a path or return a dict unchanged."""
    if isinstance(config, (str, Path)):
        with open(Path(config), encoding="utf-8") as fh:
            return json.load(fh)
    elif isinstance(config, dict):
        return config
    else:
        raise TypeError("config must be a file path or a dict")


def _find_project_root(start: Path | None = None) -> Path:
    """
    Try to find a project root by walking up from `start` (or cwd) looking for common markers.
    If none found, fall back to cwd.
    """
    markers = {"pyproject.toml", "setup.py", "setup.cfg", "Pipfile", ".git"}
    p = (start or Path.cwd()).resolve()
    for parent in [p] + list(p.parents):
        for m in markers:
            if (parent / m).exists():
                return parent
    return Path.cwd().resolve()


def _resolve_path_with_base(pathish: str | Path, base_dir: Path | None) -> Path:
    """
    Resolve a path-like value to an absolute Path.
    - If `pathish` is absolute -> returns resolved absolute Path.
    - Otherwise, if base_dir is provided, return (base_dir / pathish).resolve()
    - Else resolve relative to cwd.
    """
    p = Path(pathish)
    if p.is_absolute():
        return p.resolve()
    if base_dir is not None:
        return (base_dir / p).resolve()
    return (Path.cwd() / p).resolve()


def _collect_exported_names(cfg: dict) -> set[str]:
    """Collect the exported names from the config structure."""
    names: set[str] = set()
    for module_path, details in cfg.items():
        if not isinstance(details, dict):
            continue
        ex = details.get("exports", [])
        if isinstance(ex, Iterable):
            for e in ex:
                names.add(str(e))
    return names


def _sanitize_identifier(s: str) -> str:
    """Make a string safe for use as a Python identifier by replacing non-alphanum with underscores."""
    return re.sub(r"[^0-9a-zA-Z_]", "_", s)


def _collect_top_level_names_from_file(path: Path) -> set[str]:
    """
    Parse a .py file and collect top-level function, async function and class names.
    Returns a set of names (strings).
    """
    try:
        src = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        return set()

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        # skip files with syntax errors
        return set()

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if isinstance(node.name, str):
                names.add(node.name)
    return names


def _collect_defs_from_file(path: Path) -> dict[str, dict]:
    """Parse a file and return mapping name -> {type: 'function'|'class', params: [names], path: Path} for top-level defs."""
    result: dict[str, dict] = {}
    try:
        src = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        return result

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return result

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # get arg names (positional only, posargs, kwonly) but skip 'self' or 'cls'
            args = []
            for a in node.args.args:
                if a.arg not in ("self", "cls"):
                    args.append(a.arg)
            # include vararg/kwarg names too
            if getattr(node.args, "vararg", None) and node.args.vararg and node.args.vararg.arg not in ("self", "cls"):
                args.append(node.args.vararg.arg)
            if getattr(node.args, "kwarg", None) and node.args.kwarg and node.args.kwarg.arg not in ("self", "cls"):
                args.append(node.args.kwarg.arg)
            result[node.name] = {"type": "function", "params": args, "path": path.resolve()}
        elif isinstance(node, ast.ClassDef):
            # look for __init__ method
            init_args: list[str] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    for a in item.args.args:
                        if a.arg not in ("self", "cls"):
                            init_args.append(a.arg)
                    if getattr(item.args, "vararg", None) and item.args.vararg and item.args.vararg.arg not in ("self", "cls"):
                        init_args.append(item.args.vararg.arg)
                    if getattr(item.args, "kwarg", None) and item.args.kwarg and item.args.kwarg.arg not in ("self", "cls"):
                        init_args.append(item.args.kwarg.arg)
                    break
            result[node.name] = {"type": "class", "params": init_args, "path": path.resolve()}
    return result


def collect_defs_from_src(
    src_dir: str | Path = "src",
    exclude_dirs: Iterable[str] | None = None,
    file_pattern: str = ".py",
) -> dict[str, dict]:
    """
    Walk src_dir and return a mapping: top-level name -> dict(type, params, path)
    exclude_dirs: iterable of directory names to skip (exact match on folder name).

    Note: this function expects src_dir to be an absolute/resolved path for correct behavior.
    """
    src_dir = Path(src_dir)
    exclude_dirs = set(exclude_dirs or [])
    result: dict[str, dict] = {}

    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".venv") and not d.startswith("__pycache__")]
        root_path = Path(root)
        for f in files:
            if not f.endswith(file_pattern):
                continue
            full = (root_path / f).resolve()
            defs = _collect_defs_from_file(full)
            for name, info in defs.items():
                result[name] = info
    return result


def _expected_test_filename(name: str, prefix: str = "test_", ext: str = ".py") -> str:
    """Create expected test filename for a given name (no sanitization beyond this)."""
    return f"{prefix}{name}{ext}"


def _ensure_dir_exists(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _class_exists_in_test_source(test_src: str, class_name: str) -> bool:
    try:
        tree = ast.parse(test_src)
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return True
    return False


def _append_failing_test_classes(
    test_file: Path,
    export_name: str,
    params: list[str],
    case_sensitive: bool = True,
    test_prefix: str = "test_",
) -> tuple[bool, list[str]]:
    """Append missing test classes for (export_name, params) to test_file.
    Returns (changed, list_of_added_class_names).
    """
    created_classes: list[str] = []
    _ensure_dir_exists(test_file.parent)

    if test_file.exists():
        try:
            text = test_file.read_text(encoding="utf-8")
        except Exception:
            text = ""
    else:
        text = ""

    header_needed = text.strip() == ""
    added_text_parts: list[str] = []

    for p in params:
        if not p:
            continue
        class_name = f"Test_{_sanitize_identifier(export_name)}_{_sanitize_identifier(p)}"
        if _class_exists_in_test_source(text, class_name):
            continue
        # Prepare class source
        cls_src = f"class {class_name}(object):\n" f'    """Placeholder failing test for variable \'{p}\' of \'{export_name}\'."""\n' f"    def test_placeholder(self):\n" f"        raise NotImplementedError('Test not implemented for variable: {p} of {export_name}')\n\n\n"
        added_text_parts.append(cls_src)
        created_classes.append(class_name)

    if not added_text_parts:
        return False, []

    if header_needed:
        header = "# Auto-generated test placeholders\n# Replace with real tests\n\n"
        text = header + text

    text = text + "\n" + "".join(added_text_parts)
    try:
        test_file.write_text(text, encoding="utf-8")
    except Exception:
        return False, []
    return True, created_classes


def _create_placeholder_test_file(
    test_file: Path,
    export_name: str,
    params: list[str] | None = None,
    include_param_placeholders: bool = True,
) -> bool:
    """Create a new placeholder test file for an export or private name.
    Returns True if a file was created.
    """
    _ensure_dir_exists(test_file.parent)
    if test_file.exists():
        return False

    header = "# Auto-generated test placeholder file\n" "# Fill in real tests and remove or adjust placeholders\n\n"
    body_parts: list[str] = []

    # optional per-param placeholders
    if include_param_placeholders and params:
        for p in params:
            if not p:
                continue
            cls_name = f"Test_{_sanitize_identifier(export_name)}_{_sanitize_identifier(p)}"
            cls_src = f"class {cls_name}(object):\n" f'    """Placeholder failing test for variable \'{p}\' of \'{export_name}\'."""\n' f"    def test_placeholder(self):\n" f"        raise NotImplementedError('Test not implemented for variable: {p} of {export_name}')\n\n"
            body_parts.append(cls_src)

    content = header + "".join(body_parts) + "\n"
    try:
        test_file.write_text(content, encoding="utf-8")
        return True
    except Exception:
        return False


def ensure_test_classes_for_input_variables(
    names: set[str],
    src_defs: dict[str, dict],
    tests_dir: Path,
    test_prefix: str = "Test_",
    test_ext: str = ".py",
    case_sensitive: bool = True,
) -> dict[str, object]:
    """Ensure there is one test class per input variable for names. Create/modify files when missing.

    Returns a dict summarizing what was created/modified and missing entries.
    """
    created_files: set[str] = set()
    modified_files: set[str] = set()
    missing_var_entries: set[tuple[str, str]] = set()
    total_vars = 0
    covered_vars = 0

    for name in names:
        info = src_defs.get(name)
        if not info:
            continue
        params: list[str] = info.get("params", [])
        total_vars += len([p for p in params if p])
        if not params:
            continue
        test_filename = _expected_test_filename(name, test_prefix, test_ext)
        test_file_path = tests_dir / test_filename

        # read existing classes to determine coverage
        existing_src = ""
        if test_file_path.exists():
            try:
                existing_src = test_file_path.read_text(encoding="utf-8")
            except Exception:
                existing_src = ""

        for p in params:
            if not p:
                continue
            class_name = f"Test_{_sanitize_identifier(name)}_{_sanitize_identifier(p)}"
            exists = _class_exists_in_test_source(existing_src, class_name) if existing_src else False
            if exists:
                covered_vars += 1
            else:
                missing_var_entries.add((name, p))

        # append placeholder classes for missing params
        missing_for_file = [p for p in params if not _class_exists_in_test_source(existing_src, f"Test_{_sanitize_identifier(name)}_{_sanitize_identifier(p)}")]
        if missing_for_file:
            changed, created_classes = _append_failing_test_classes(test_file_path, name, missing_for_file, case_sensitive, test_prefix)
            if changed:
                # determine whether this was a create vs modify
                if test_file_path.exists() and existing_src:
                    modified_files.add(str(test_file_path.resolve()))
                else:
                    created_files.add(str(test_file_path.resolve()))
                covered_vars += len(created_classes)

    coverage_pct = (covered_vars / total_vars * 100.0) if total_vars else 100.0

    return {
        "created_files": created_files,
        "modified_files": modified_files,
        "missing_var_entries": {f"{n}:{p}" for (n, p) in missing_var_entries},
        "counts": {"total_vars": total_vars, "covered_vars": covered_vars},
        "coverage_pct": round(coverage_pct, 2),
    }


def collect_top_level_names_from_src(
    src_dir: str | Path = "src",
    exclude_dirs: Iterable[str] | None = None,
    file_pattern: str = ".py",
) -> dict[Path, set[str]]:
    """
    Walk src_dir and return a mapping: filepath -> set(top-level names)
    exclude_dirs: iterable of directory names to skip (exact match on folder name).

    Note: this function expects src_dir to be an absolute/resolved path for correct behavior.
    """
    src_dir = Path(src_dir)
    exclude_dirs = set(exclude_dirs or [])
    result: dict[Path, set[str]] = {}

    for root, dirs, files in os.walk(src_dir):
        # prune excluded directories (matching directory names)
        # mutate dirs in-place so os.walk won't descend into them
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".venv") and not d.startswith("__pycache__")]
        root_path = Path(root)
        for f in files:
            if not f.endswith(file_pattern):
                continue
            full = (root_path / f).resolve()
            names = _collect_top_level_names_from_file(full)
            if names:
                result[full] = names
    return result


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
) -> dict[str, object]:
    """
    Check that every exported name from config has a corresponding test file in tests_dir,
    and optionally scan src_dir for private top-level names (leading underscore) that are not
    in the config and report their test coverage. Additionally, when auto_create_missing_input_var_tests
    is True it ensures there is one test class per input variable (parameter) of exported and internal functions/classes
    and will create/update test files with failing placeholder tests for missing ones.

    When auto_create_missing_test_files is True the function will also create missing test files for
    exported names or private names that currently have no test file at all (useful for exports without params).
    """
    # Determine a sensible base directory to resolve relative paths.
    if isinstance(config, (str, Path)):
        cfg_path = Path(config)
        if not cfg_path.is_absolute():
            cfg_path = _resolve_path_with_base(cfg_path, _find_project_root())
        if cfg_path.exists():
            base_dir = cfg_path.resolve().parent
        else:
            base_dir = _find_project_root()
    else:
        base_dir = _find_project_root()

    # Resolve src_dir and tests_dir relative to base_dir (or absolute if already absolute)
    src_dir = _resolve_path_with_base(src_dir, base_dir)

    # Handle tests_dir: single path or tuple for (api, private)
    if isinstance(tests_dir, tuple):
        api_tests_dir = _resolve_path_with_base(tests_dir[0], base_dir)
        private_tests_dir = _resolve_path_with_base(tests_dir[1], base_dir)
    else:
        api_tests_dir = _resolve_path_with_base(tests_dir, base_dir)
        private_tests_dir = api_tests_dir

    cfg = _load_config(config)
    exported_names = _collect_exported_names(cfg)

    try:
        actual_list = list(api_tests_dir.iterdir())
    except FileNotFoundError:
        actual_list = []
    actual_test_files = {p.name for p in actual_list if p.is_file() and p.name.startswith(test_prefix) and p.name.endswith(test_ext)}

    # Build expected test filenames for exported names
    expected_export_files = {_expected_test_filename(name, test_prefix, test_ext) for name in exported_names}

    # compare with optional case insensitivity
    if not case_sensitive:
        expected_export_lower = {s.lower() for s in expected_export_files}
        actual_lower = {s.lower() for s in actual_test_files}
        missing_export_lower = expected_export_lower - actual_lower
        extra_lower = actual_lower - expected_export_lower

        def map_back(lower_set: set[str], original_set: set[str]) -> set[str]:
            mapping = {s.lower(): s for s in original_set}
            return {mapping[l] for l in lower_set if l in mapping}

        exports_missing_files = map_back(missing_export_lower, expected_export_files)
        extra_test_files = map_back(extra_lower, actual_test_files)
    else:
        exports_missing_files = expected_export_files - actual_test_files
        extra_test_files = actual_test_files - expected_export_files

    # Now scan src for private top-level names (and optionally all top-level names)
    private_names_found: set[str] = set()
    private_missing_test_files: set[str] = set()
    private_total = 0
    private_covered = 0

    # Collect defs map to inspect input variables for exported names
    src_defs = collect_defs_from_src(src_dir=src_dir, exclude_dirs=exclude_dirs)

    if include_private:
        src_map = collect_top_level_names_from_src(src_dir=src_dir, exclude_dirs=exclude_dirs)
        # collect private top-level names (leading underscore) that are not declared in config exports
        for path, names in src_map.items():
            for n in names:
                if n.startswith("_") and n not in exported_names:
                    private_names_found.add(n)

        # For each private name, check test existence
        expected_private_files = {_expected_test_filename(name, test_prefix, test_ext) for name in private_names_found}

        try:
            private_list = list(private_tests_dir.iterdir())
        except FileNotFoundError:
            private_list = []
        actual_test_files_private = {p.name for p in private_list if p.is_file() and p.name.startswith(test_prefix) and p.name.endswith(test_ext)}

        if not case_sensitive:
            expected_private_lower = {s.lower() for s in expected_private_files}
            actual_private_lower = {s.lower() for s in actual_test_files_private}
            missing_private_lower = expected_private_lower - actual_private_lower

            mapping = {s.lower(): s for s in expected_private_files}
            private_missing_test_files = {mapping[l] for l in missing_private_lower if l in mapping}
            private_covered = len(expected_private_files) - len(private_missing_test_files)
            private_total = len(expected_private_files)
        else:
            private_missing_test_files = expected_private_files - actual_test_files_private
            private_covered = len(expected_private_files) - len(private_missing_test_files)
            private_total = len(expected_private_files)

    # --- Auto-create missing test files for exports (useful for exports with no params)
    created_placeholder_files: set[str] = set()
    if auto_create_missing_test_files:
        # create missing export test files
        for export_name in exported_names:
            expected_filename = _expected_test_filename(export_name, test_prefix, test_ext)
            # skip if file already present (respect case sensitivity by checking sets earlier)
            if expected_filename in actual_test_files:
                continue
            test_file_path = api_tests_dir / expected_filename
            # params for this export if available
            info = src_defs.get(export_name)
            params = info.get("params") if info else None
            created = _create_placeholder_test_file(test_file_path, export_name, params=params, include_param_placeholders=False)
            if created:
                created_placeholder_files.add(str(test_file_path.resolve()))
                actual_test_files.add(expected_filename)

        # create missing private test files
        if include_private:
            for private_name in private_names_found:
                expected_filename = _expected_test_filename(private_name, test_prefix, test_ext)
                if expected_filename in actual_test_files_private:
                    continue
                test_file_path = private_tests_dir / expected_filename
                info = src_defs.get(private_name)
                params = info.get("params") if info else None
                created = _create_placeholder_test_file(test_file_path, private_name, params=params, include_param_placeholders=False)
                if created:
                    created_placeholder_files.add(str(test_file_path.resolve()))

    # Optionally, ensure there is a test class per input variable of exported names
    input_var_check_summary_exports = {}
    if auto_create_missing_input_var_tests:
        input_var_check_summary_exports = ensure_test_classes_for_input_variables(
            names=exported_names,
            src_defs=src_defs,
            tests_dir=api_tests_dir,
            test_prefix=test_prefix,
            test_ext=test_ext,
            case_sensitive=case_sensitive,
        )

    input_var_check_summary_private = {}
    if include_private and auto_create_missing_input_var_tests:
        input_var_check_summary_private = ensure_test_classes_for_input_variables(
            names=private_names_found,
            src_defs=src_defs,
            tests_dir=private_tests_dir,
            test_prefix=test_prefix,
            test_ext=test_ext,
            case_sensitive=case_sensitive,
        )

    # Build coverage summary
    export_total = len(expected_export_files)
    export_missing = len(exports_missing_files)
    export_covered = max(export_total - export_missing, 0)
    export_coverage_pct = (export_covered / export_total * 100.0) if export_total else 100.0

    private_coverage_pct = (private_covered / private_total * 100.0) if private_total else 100.0

    overall_total = export_total + private_total
    overall_covered = export_covered + private_covered
    overall_coverage_pct = (overall_covered / overall_total * 100.0) if overall_total else 100.0

    result = {
        "exports_expected_files": expected_export_files,
        "exports_actual_files": actual_test_files,
        "exports_missing_files": exports_missing_files,
        "extra_test_files": extra_test_files,
        "private_names_found": private_names_found,
        "private_missing_test_files": private_missing_test_files,
        "counts": {
            "exports_total": export_total,
            "exports_missing": export_missing,
            "exports_covered": export_covered,
            "private_total": private_total,
            "private_missing": len(private_missing_test_files),
            "private_covered": private_covered,
            "overall_total": overall_total,
            "overall_covered": overall_covered,
        },
        "coverage": {
            "exports_pct": round(export_coverage_pct, 2),
            "private_pct": round(private_coverage_pct, 2),
            "overall_pct": round(overall_coverage_pct, 2),
        },
        "input_variable_checks_exports": input_var_check_summary_exports,
        "input_variable_checks_private": input_var_check_summary_private,
        "created_placeholder_files": created_placeholder_files,
    }

    # Friendly printout
    print("=== test existence & private-coverage check ===")
    print("config.py: ", config)
    print(f"Base dir used to resolve relative paths: {base_dir}")
    print(f"API Tests folder: {api_tests_dir.resolve()}")
    print(f"Private Tests folder: {private_tests_dir.resolve()}\n")

    print(f"config.py API: {export_total}")
    print(f"Exports covered: {export_covered}/{export_total} ({result['coverage']['exports_pct']}%)")
    if exports_missing_files:
        print(f"\nMissing export test files ({len(exports_missing_files)}):")
        for m in sorted(exports_missing_files):
            print("  -", m)

    print()
    print(f"Private names discovered (leading underscore, not listed in config): {len(private_names_found)}")
    print(f"Private covered: {private_covered}/{private_total} ({result['coverage']['private_pct']}%)")
    if private_missing_test_files:
        print(f"\nMissing private test files ({len(private_missing_test_files)}):")
        for m in sorted(private_missing_test_files):
            print("  -", m)

    if extra_test_files:
        print(f"\nExtra test files (present in tests dir but not expected for exports): {len(extra_test_files)}")
        for e in sorted(extra_test_files):
            print("  -", e)

    if created_placeholder_files:
        print()
        print(f"Created placeholder test files: {len(created_placeholder_files)}")
        for f in sorted(created_placeholder_files):
            print("  -", f)

    print()
    if input_var_check_summary_exports:
        print("Input-variable test coverage for exports:")
        print(f"  total variables: {input_var_check_summary_exports.get('counts', {}).get('total_vars', 0)}")
        print(f"  covered variables: {input_var_check_summary_exports.get('counts', {}).get('covered_vars', 0)}")
        print(f"  coverage: {input_var_check_summary_exports.get('coverage_pct', 0.0)}%")
        if input_var_check_summary_exports.get("created_files"):
            print(f"  Created test files: {len(input_var_check_summary_exports.get('created_files'))}")
            for f in sorted(input_var_check_summary_exports.get("created_files") or []):
                print("    -", f)
        if input_var_check_summary_exports.get("modified_files"):
            print(f"  Modified test files: {len(input_var_check_summary_exports.get('modified_files'))}")
            for f in sorted(input_var_check_summary_exports.get("modified_files") or []):
                print("    -", f)

    if input_var_check_summary_private:
        print("Input-variable test coverage for private/internal functions:")
        print(f"  total variables: {input_var_check_summary_private.get('counts', {}).get('total_vars', 0)}")
        print(f"  covered variables: {input_var_check_summary_private.get('counts', {}).get('covered_vars', 0)}")
        print(f"  coverage: {input_var_check_summary_private.get('coverage_pct', 0.0)}% \n")
        if input_var_check_summary_private.get("created_files"):
            print(f"  Created test files: {len(input_var_check_summary_private.get('created_files'))}")
            for f in sorted(input_var_check_summary_private.get("created_files") or []):
                print("    -", f)
        if input_var_check_summary_private.get("modified_files"):
            print(f"  Modified test files: {len(input_var_check_summary_private.get('modified_files'))}")
            for f in sorted(input_var_check_summary_private.get("modified_files") or []):
                print("    -", f)

    print(f"Overall coverage (exports + private): {result['coverage']['overall_pct']}% ({overall_covered}/{overall_total})")
    print("===============================================")
    if overall_coverage_pct < 100:
        raise ValueError("Test coverage check failed")
    return result
