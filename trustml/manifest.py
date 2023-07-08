import logging
from pathlib import Path
from typing import List


log = logging.getLogger("trustml")


class Manifest:
    def __init__(self, manifest_file: str) -> None:
        self.manifest_file = Path(manifest_file)

    def _check_exists(self) -> bool:
        if not self.manifest_file.exists():
            log.error(f"The manifest file '{self.manifest_file}' " \
                      "doesn't exist.")
            return False
        return True

    def _check_has_files(self, file_list: List[str]) -> bool:
        if len(file_list) <= 0:
            log.error(f"The manifest file '{self.manifest_file}' "
                      "has no files listed.")
            return False
        return True

    def _check_files_exist(self, file_list: List[str]) -> bool:
        file_list = self.get_files()
        for file_name in file_list:
            fpath = Path(file_name)
            if not fpath.exists():
                log.error(f"The file '{fpath}' listed in the manifest"
                          f" '{self.manifest_file}' doesn't exist.")
                return False
        return True

    def get_files(self) -> List[str]:
        with self.manifest_file.open("r") as fh:
            manifest_data = fh.read().strip()
        manifest_files = manifest_data.splitlines()
        return manifest_files

    def verify_consistency(self) -> bool:
        exist = self._check_exists()
        if not exist:
            return False

        file_list = self.get_files()
        has_files = self._check_has_files(file_list)
        files_exist = self._check_files_exist(file_list)
        return has_files and files_exist
