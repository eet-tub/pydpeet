from pathlib import Path

from pydpeet._dev_utils.check_test_coverge.check_test_coverage import (
    _print_report,
    check_tests_and_generate_missing_test_files,
)


class TestCoverage:
    def test_full_coverage(self):
        project_root = Path(__file__).resolve().parents[2]

        config_path = project_root / "src/pydpeet/_dev_utils/generate_inits/config.json"
        api_tests = project_root / "test/api_accessible"
        private_tests = project_root / "test/internal"
        src_dir = project_root / "src"

        common_kwargs = dict(
            config=config_path,
            tests_dir=(api_tests, private_tests),
            src_dir=src_dir,
            exclude_dirs=["_dev_utils", "res"],
            test_prefix="test_",
            test_ext=".py",
            case_sensitive=True,
            include_private=True,
            print_report=False,
        )

        before = check_tests_and_generate_missing_test_files(
            **common_kwargs,
            auto_create_missing_test_files=False,
            auto_create_missing_input_var_tests=False,
        )

        after = check_tests_and_generate_missing_test_files(
            **common_kwargs,
            auto_create_missing_test_files=True,
            auto_create_missing_input_var_tests=True,
        )

        # 1) Files / folders
        print(f"config.py: {config_path}")
        print(f"Base dir: {project_root}")
        print(f"API Tests folder: {api_tests}")
        print(f"Private Tests folder: {private_tests}\n")

        # 2) Table before
        print("--- BEFORE ---")
        _print_report(config_path, project_root, api_tests, private_tests, before, phase="before")
        print()

        # 3) Changes
        print("--- CHANGES ---")
        _print_report(config_path, project_root, api_tests, private_tests, after, phase="changes")
        print()

        # 4) Table after + 5) Duplicates
        print("--- AFTER ---")
        _print_report(config_path, project_root, api_tests, private_tests, after, phase="after")

        # Fail if placeholders were generated
        created = after.get("created_placeholder_files", set())
        modified = after.get("modified_files", set())
        if created or modified:
            raise AssertionError(
                f"Test coverage placeholders were auto-generated.\n"
                f"Created: {len(created)} file(s), Modified: {len(modified)} file(s)\n"
                f"Implement the tests and commit again."
            )
