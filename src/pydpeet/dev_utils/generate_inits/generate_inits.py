#!/usr/bin/env python3
"""
Init generator
- Deletes all existing __init__.py under the package root
- Creates restrictive __init__.py everywhere
- Applies config.json to expose only the listed functions at the requested package depth

expects config.json in format:
    {
      "src/pydpeet/convert/convert.py": {
        "depth": 4,
        "exports": ["convert_file"]
      },
      ...
    }

this will enable this import:
    import pydpeet as eet
    eet.convert.convert_file(...)
"""

import datetime
import json
import os
import sys

CONFIG_FILENAME = "config.json"
LOG_FILENAME = "generation_log.txt"


def get_script_path():
    return os.path.abspath(__file__)


def get_script_dir():
    return os.path.dirname(get_script_path())


def header_text():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f'"""\nAuto-generated __init__ file.\nCreated: {timestamp}\n"""\n\n'


class Logger:
    def __init__(self, filename):
        self.filepath = os.path.join(get_script_dir(), filename)
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(f"--- Init Generation Log: {datetime.datetime.now()} ---\n\n")

    def log(self, message):
        print(message)
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(message + "\n")


def find_project_and_package_root(start_path, logger):
    """
    Walk up until we find a pyproject.toml (project root).
    If a 'src' folder exists in the project root we treat project_root/src as package_root.
    Otherwise package_root == project_root.
    """
    current = start_path
    while True:
        if os.path.exists(os.path.join(current, "pyproject.toml")):
            project_root = current
            src_path = os.path.join(project_root, "src")
            package_root = src_path if os.path.isdir(src_path) else project_root
            logger.log(f"Project root: {project_root}")
            logger.log(f"Package root: {package_root}")
            return project_root, package_root
        parent = os.path.dirname(current)
        if parent == current:
            # reached filesystem root, fallback
            logger.log("No pyproject.toml found; using script dir as project_root/package_root")
            return start_path, start_path
        current = parent


def remove_all_inits(root_dir, logger):
    """Delete every existing __init__.py under root_dir"""
    logger.log("--- PHASE 1: Deleting all existing __init__.py files ---")
    removed = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn == "__init__.py":
                p = os.path.join(dirpath, fn)
                try:
                    os.remove(p)
                    removed += 1
                except Exception as e:
                    logger.log(f"Failed to remove {p}: {e}")
    logger.log(f"Removed {removed} existing __init__.py files.")


def create_empty_inits(root_dir, logger):
    """
    Create an __init__.py for every folder under root_dir with strict empty __all__.
    This ensures no accidental exports by existing modules.
    """
    logger.log("--- PHASE 2: Creating restrictive empty __init__.py across tree ---")
    created = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # skip hidden dirs and __pycache__
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]
        init_path = os.path.join(dirpath, "__init__.py")
        try:
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(header_text())
                f.write("# Restrictive package init: start with no public API\n")
                f.write("__all__ = []\n")
            created += 1
        except Exception as e:
            logger.log(f"Failed to create {init_path}: {e}")
    logger.log(f"Created {created} new restrictive __init__.py files.")


def module_dotted_from_path(abs_path, project_root, package_root):
    """
    Return the full dotted module path for a .py file relative to package_root.
    e.g. abs_path -> /.../project/src/pydpeet/convert/directory_standardization.py
    package_root -> /.../project/src
    returns -> 'pydpeet.convert.directory_standardization'
    """
    rel = os.path.relpath(abs_path, package_root)
    parts = rel.split(os.sep)
    if parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def apply_config(project_root, package_root, config_path, logger):
    logger.log("--- PHASE 3: Applying config.json to build the public API ---")
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    # mapping: dir_path -> { 'child_packages': set(child_name),
    #                        'module_imports': { full_module_dotted: set(export_names) },
    #                        'exports': set(function_and_child_names) }
    dir_data = {}

    def get_data_for_dir(dir_path):
        if dir_path not in dir_data:
            dir_data[dir_path] = {
                "child_packages": set(),
                "module_imports": {},  # module_dotted -> set(names)
                "exports": set(),
            }
        return dir_data[dir_path]

    for rel_path, settings in config.items():
        exports = settings.get("exports", [])
        depth = settings.get("depth")
        if not isinstance(depth, int) or depth < 1:
            logger.log(f"Invalid depth for {rel_path}: {depth} (must be int >=1); skipping")
            continue

        source_abs_path = os.path.abspath(os.path.join(project_root, rel_path))
        if not os.path.exists(source_abs_path):
            logger.log(f"WARNING: file not found: {source_abs_path}; skipping")
            continue

        # Build rel parts from project root (so depth param matches your config's notion)
        rel_parts_from_project = os.path.relpath(source_abs_path, project_root).split(os.sep)
        # target folder parts are first (depth - 1) entries
        target_folder_parts = rel_parts_from_project[: max(1, depth - 1)]
        # if package_root is project_root/src, drop that first element if it equals basename(package_root)
        if os.path.normpath(package_root).endswith(os.path.sep + target_folder_parts[0]) or (
            target_folder_parts[0] == os.path.basename(package_root)
        ):
            # remove the leading package root element if present (common case with 'src')
            pkg_parts = target_folder_parts[1:]
        else:
            # general case: target package parts are target_folder_parts starting at 0,
            # but if the first entry was 'src' (rare if package_root != project_root) handle below
            if target_folder_parts[0] == "src":
                pkg_parts = target_folder_parts[1:]
            else:
                pkg_parts = target_folder_parts

        if not pkg_parts:
            # exporting at the package root
            target_package_dotted = ""  # special case
            target_dir = package_root
        else:
            target_package_dotted = ".".join(pkg_parts)
            target_dir = os.path.join(package_root, *pkg_parts)

        # Determine full module dotted name relative to package root
        module_dotted = module_dotted_from_path(source_abs_path, project_root, package_root)

        # Add the function exports to the target_dir data
        ddata = get_data_for_dir(target_dir)
        ddata["module_imports"].setdefault(module_dotted, set()).update(exports)
        ddata["exports"].update(exports)

        # Bubble up: mark parent dirs to import child packages (so top-level 'pydpeet' exposes 'convert', etc.)
        # walk parents until package_root (inclusive)
        curr = target_dir
        # if target_dir is package_root, still possibly export module names directly at package_root
        while True:
            parent = os.path.dirname(curr)
            if parent == curr:
                break
            if os.path.commonpath([package_root, curr]) != os.path.normpath(package_root) and not curr.startswith(
                os.path.normpath(package_root)
            ):
                # outside of package_root, stop
                break
            # compute child name (basename of curr) relative to parent
            child_name = os.path.basename(curr)
            if child_name == "":
                break
            if parent.startswith(package_root) or os.path.normpath(parent) == os.path.normpath(package_root):
                # ensure parent has data
                p_data = get_data_for_dir(parent)
                # Parent should expose the child package name (so importers can reference pydpeet.convert)
                p_data["child_packages"].add(child_name)
                p_data["exports"].add(child_name)
            if os.path.normpath(curr) == os.path.normpath(package_root):
                break
            curr = parent
            if os.path.normpath(curr) == os.path.normpath(os.path.dirname(package_root)):
                break

    # Now write the __init__.py files for each dir in dir_data (overwrite the existing restrictive ones)
    for dir_path, data in dir_data.items():
        init_path = os.path.join(dir_path, "__init__.py")
        # ensure the dir exists
        os.makedirs(dir_path, exist_ok=True)
        try:
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(header_text())
                # child package imports (so parent exposes child as attribute)
                if data["child_packages"]:
                    f.write("# Child packages exported by this package\n")
                    for child in sorted(data["child_packages"]):
                        f.write(f"from . import {child}\n")
                    f.write("\n")

                # module imports -> bind functions into this package WITHOUT leaving the submodule object as an attribute
                # inside the loop that writes the __init__.py file for dir_path:

                # --- static re-export approach ---
                if data["module_imports"]:
                    f.write("# Re-export selected names from source modules\n\n")
                    # module_imports is mapping full_module_dotted -> set(names)
                    for mod in sorted(data["module_imports"].keys()):
                        names = sorted(data["module_imports"][mod])
                        # Write a single `from <module> import a, b, c` line per module
                        # Use explicit imports only for the configured names
                        f.write(f"from {mod} import {', '.join(names)}\n")
                    f.write("\n")

                # Write __all__
                all_entries = sorted(data["exports"])
                f.write("# Public API for this package\n")
                f.write("__all__ = [\n")
                for ent in all_entries:
                    f.write(f"    '{ent}',\n")
                f.write("]\n")
            logger.log(f"Written public API for: {os.path.relpath(dir_path, package_root)}")
        except Exception as e:
            logger.log(f"Failed to write {init_path}: {e}")

    # Ensure package_root has an __init__ that exports top-level packages (e.g., 'pydpeet')
    root_data = get_data_for_dir(package_root)
    # If package root did not get any auto exports (possible), build sensible top-level __init__
    # but don't overwrite if a specific config already created explicit exports
    init_root = os.path.join(package_root, "__init__.py")
    if os.path.exists(init_root):
        # augment: ensure __all__ includes folders with exports present under package_root
        # find immediate child dirs with dir_data entries
        child_packages = set()
        for p in dir_data.keys():
            try:
                rel = os.path.relpath(p, package_root).split(os.sep)
                if len(rel) >= 1 and rel[0] != ".":
                    child_packages.add(rel[0])
            except Exception:
                continue
        # read the file and update __all__ if needed
        try:
            with open(init_root, encoding="utf-8") as f:
                content = f.read()
            # simplistic append if not present
            if child_packages:
                # create an augmented root __init__ that imports child packages and sets __all__
                with open(init_root, "w", encoding="utf-8") as f:
                    f.write(header_text())
                    f.write("# Expose immediate child packages at package root\n")
                    for child in sorted(child_packages):
                        f.write(f"from . import {child}\n")
                    f.write("\n")
                    f.write("__all__ = [\n")
                    for child in sorted(child_packages):
                        f.write(f"    '{child}',\n")
                    f.write("]\n")
                logger.log("Updated package root __init__ to export immediate child packages.")
        except Exception as e:
            logger.log(f"Failed updating package root __init__: {e}")


def main():
    logger = Logger(LOG_FILENAME)
    script_dir = get_script_dir()
    project_root, package_root = find_project_and_package_root(script_dir, logger)

    # Phase 1: delete all old inits
    remove_all_inits(package_root, logger)

    # Phase 2: create empty restrictive inits everywhere
    create_empty_inits(package_root, logger)

    # Phase 3: apply config
    config_path = os.path.join(script_dir, CONFIG_FILENAME)
    if not os.path.exists(config_path):
        logger.log(f"Config file not found at {config_path}. Aborting.")
        sys.exit(1)

    apply_config(project_root, package_root, config_path, logger)
    logger.log("\n--- Done ---\n")


if __name__ == "__main__":
    main()
