import logging
from pathlib import Path
from typing import cast

import click
import jwt
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from sigstore.oidc import Issuer
from sigstore.sign import SigningContext

import trustml
from trustml.manifest import Manifest
from trustml.truststore import TrustStore

from sigstore.verify import Verifier
from sigstore.verify import policy, VerificationFailure


log = logging.getLogger("trustml")
console = Console()


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug: bool) -> None:
    # Setup logging according to debug level
    log_level = "DEBUG" if debug else "INFO"
    # Bug in rich, we need to reduce by one the width
    console.width = console.width - 1
    logging.basicConfig(
        level=log_level, format="%(message)s",
        datefmt="[%X]", handlers=[RichHandler(markup=True,
                                              console=console)]
    )
    # Version banner
    version = trustml.__version__
    year = trustml.__year__
    log.info(f"🔐 [bold green]trustml v{version} ({year})[/]",
             extra={"highlighter": None})


@main.command()
@click.option("--manifest", default="manifest.trustml",
              help="input manifest file",
              show_default=True, type=click.Path(exists=True))
@click.option("--truststore", "-t", "storename", default="truststore.trustml",
              help="output trustml store (with certificates)",
              show_default=True, type=click.Path())
def sign(manifest: str, storename: str) -> None:
    # Get manifest file list
    manifest_manager = Manifest(manifest)
    consistent = manifest_manager.verify_consistency()
    if not consistent:
        raise RuntimeError("Manifest consistency check failed.")
    manifest_files = manifest_manager.get_files()
    log.info(f"🗂 Found {len(manifest_files)} files in the manifest.")

    issuer = Issuer.staging()
    log.info("🪪 Starting identity workflow.")
    identity = issuer.identity_token()

    jwt_header = jwt.get_unverified_header(str(identity))
    log.info(f"✅ Identity token confirmed "
             f"([bold]{identity.identity} / {jwt_header['alg']}[/bold]).")
    log.info(f"Expected certificate subject: "
             f"[bold]{identity.expected_certificate_subject}.")

    log.info("🔏 Signing manifest files:")
    total_files = len(manifest_files)

    with Progress(
        SpinnerColumn(speed=2.0),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        transient=True,
        console=console,
    ) as progress:
        task_sign = progress.add_task("[green]Signing", total=total_files)

        trust_store = TrustStore()
        for filename in manifest_files:
            fpath = Path(filename)
            log.info(f"\tSigning file '{fpath}'.")
            with fpath.open("rb") as file:
                signing_ctx = SigningContext.staging()
                with signing_ctx.signer(identity, cache=True) as signer:
                    result = signer.sign(file)
                    bundle = result._to_bundle()
                    trust_store.add_bundle(fpath, bundle)
                    progress.update(task_sign, advance=1)

    pstorename = Path(storename)
    with pstorename.open("w") as shandle:
        trust_store.to_json(shandle)
    log.info(f"🔐 Saved certificates/signatures into '{pstorename}'.")


@main.command()
@click.option("--truststore", "-t", "storename", default="truststore.trustml",
              help="output trustml store (with certificates)",
              show_default=True, type=click.Path(exists=True))
def inspect(storename: str) -> None:
    pstorename = Path(storename)
    with pstorename.open("r") as shandle:
        trust_store = TrustStore.from_json(shandle)
    log.info(f"Loaded trust store with {len(trust_store)} items.")


@main.command()
@click.option("--truststore", "-t", "storename", default="truststore.trustml",
              help="output trustml store (with certificates)",
              show_default=True, type=click.Path(exists=True),
              required=True)
@click.option("--identity", help="identity to verify against",
              required=True)
@click.option("--issuer", help="OIDC issuer to verify against",
              default="https://accounts.google.com",
              show_default=True, required=True)
def verify(storename: str, identity: str, issuer: str) -> None:
    pstorename = Path(storename)
    with pstorename.open("r") as shandle:
        trust_store = TrustStore.from_json(shandle)
    log.info(f"Loaded trust store with {len(trust_store)} items.")

    verifier = Verifier.staging()
    policy_ = policy.Identity(identity=identity, issuer=issuer)

    log.info("Creating verification data for each item.")
    vmaterials = trust_store.to_verification_material(offline=False)

    log.info("⌛ Verifying each item in trust store:")
    total_files = len(vmaterials)

    with Progress(
        SpinnerColumn(speed=2.0),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        transient=True,
        console=console,
    ) as progress:
        task_verify = progress.add_task("[green]Verifying", total=total_files)
        for trust_entry in vmaterials:
            result = verifier.verify(
                materials=trust_entry.verification_material,
                policy=policy_
            )
            if result.success:
                log.info(f"✅ [bold]{trust_entry.filename} OK[/bold]")
            else:
                failure = cast(VerificationFailure, result)
                reason = failure.reason
                log.info(f"❌ [bold]{trust_entry.filename}[/bold] ({reason})")
            progress.update(task_verify, advance=1)
