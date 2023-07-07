import json
import os
import pathlib
from typing import Union

from sigstore_protobuf_specs.dev.sigstore.bundle.v1 import Bundle


class TrustStore:
    def __init__(self) -> None:
        self.bundle_map = {}

    def add_bundle(self, filename: Union[str, os.PathLike],
                   bundle: Bundle):
        self.bundle_map[filename] = bundle.to_dict()

    def to_json(self, stream):
        json.dump(self.bundle_map, stream)

    def from_json(self, stream):
        pass

    def __len__(self) -> int:
        return len(self.bundle_map)
