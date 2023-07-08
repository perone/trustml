import json
import os
from typing import Dict, Optional, TextIO, TypeAlias, Union

from sigstore_protobuf_specs.dev.sigstore.bundle.v1 import Bundle

BundleMap: TypeAlias = Dict[str, Dict]


class TrustStore:
    VERSION = 1

    def __init__(self,
                 bundle_map: Optional[BundleMap] = None) -> None:
        self.bundle_map: BundleMap = bundle_map or {}

    def add_bundle(self, filename: Union[str, os.PathLike],
                   bundle: Bundle) -> None:
        fnamestr = str(filename)
        self.bundle_map[fnamestr] = bundle.to_dict()

    def to_json(self, stream: TextIO) -> None:
        json.dump({
            "bundle_map": self.bundle_map,
            "version": TrustStore.VERSION,
        }, stream)

    @staticmethod
    def from_json(stream: TextIO) -> 'TrustStore':
        json_data = json.load(stream)
        version = json_data["version"]
        if version > TrustStore.VERSION:
            raise RuntimeError(f"Unsupported version: "
                               f"{version} > {TrustStore.VERSION}.")
        bundle_map = json_data["bundle_map"]
        return TrustStore(bundle_map)

    def __len__(self) -> int:
        return len(self.bundle_map)
