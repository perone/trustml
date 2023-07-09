import json
import os
from pathlib import Path
from typing import Dict, List, Optional, TextIO, TypeAlias, Union
from dataclasses import dataclass

from sigstore_protobuf_specs.dev.sigstore.bundle.v1 import Bundle
from sigstore.verify import VerificationMaterials

BundleMap: TypeAlias = Dict[str, Dict]


@dataclass
class TrustStoreEntry:
    filename: str
    verification_material: VerificationMaterials


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

    def to_verification_material(self,
                                 offline: bool = False
                                 ) -> List[TrustStoreEntry]:
        verification_materials: List[TrustStoreEntry] = []
        for filename, bundle_dict in self.bundle_map.items():
            bundle = Bundle().from_dict(bundle_dict)
            pfilename = Path(filename)
            with pfilename.open(mode="rb", buffering=0) as fh:
                materials = VerificationMaterials.from_bundle(input_=fh,
                                                              bundle=bundle,
                                                              offline=offline)
                entry = TrustStoreEntry(filename, materials)
                verification_materials.append(entry)
        return verification_materials

    def __len__(self) -> int:
        return len(self.bundle_map)
