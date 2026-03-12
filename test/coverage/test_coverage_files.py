from pathlib import Path

from pydpeet.dev_utils.check_test_coverge.check_test_coverage import check_tests_and_generate_missing_test_files


class TestCoverage:
    def test_full_coverage(self):
        project_root = Path(__file__).resolve().parents[2]

        config_path = project_root / "src/pydpeet/dev_utils/generate_inits/config.json"
        api_tests = project_root / "test/api_accessible"
        private_tests = project_root / "test/internal"
        src_dir = project_root / "src"

        try:
            _ = check_tests_and_generate_missing_test_files(
                config=config_path,
                tests_dir=(api_tests, private_tests),
                src_dir=src_dir,
                exclude_dirs=["dev_utils", "res"],
                test_prefix="test_",
                test_ext=".py",
                case_sensitive=True,
                include_private=True,
                auto_create_missing_test_files=True,
                auto_create_missing_input_var_tests=True,
            )
        except Exception as e:
            if e == "ValueError":
                msg = "the test should work on rerun since it automatically creates the missing test files and classes with placeholders"
                raise AssertionError(f"Test failed with error: {e}. {msg} \n")
            raise AssertionError(f"Test failed with error: {e} \n")
