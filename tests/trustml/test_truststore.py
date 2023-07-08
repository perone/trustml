from pathlib import Path

from sigstore_protobuf_specs.dev.sigstore.bundle.v1 import Bundle

from trustml.truststore import TrustStore


def test_add_bundle(datadir):
    bundlepath = datadir / "test_artifact.txt.sigstore"
    with bundlepath.open("r") as fh:
        data = fh.read()
    bundle1 = Bundle().from_json(data)
    bundle2 = Bundle().from_json(data)

    ts = TrustStore()
    ts.add_bundle("a", bundle1)
    ts.add_bundle("b", bundle2)

    with Path("/tmp/tt.json").open("w") as fh:
        ts.to_json(fh)

    with Path("/tmp/tt.json").open("r") as fh:
        ts2 = TrustStore.from_json(fh)
