from pathlib import Path


class ExtPath(Path):
    @staticmethod
    def is_not_valid(path: str | None) -> bool:
        """
        Checks if a given path is not valid.

        Args:
            path (str | None): The path to check.

        Returns:
            bool: True if the path is not valid; False otherwise.
        """
        return not ExtPath.is_valid(path)

    @staticmethod
    def is_valid(path: str | None) -> bool:
        """
        Checks if a given path is valid.

        A path is valid if it is not None or empty and if it exists.

        Args:
            path (str | None): The path to check.

        Returns:
            bool: True if the path is valid; False otherwise.
        """
        if path is None or path == "":
            return False
        return Path(path).exists()

    def is_excel_file(self) -> bool:
        return self.exists() and self.is_file() and self.suffix in (".xlsx", ".xls")
