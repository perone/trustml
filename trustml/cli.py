import logging

import click
import jwt
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from sigstore.oidc import Issuer
from sigstore.sign import SigningContext
from rich.console import Console
from pathlib import Path

import trustml
from trustml.manifest import Manifest
from trustml.truststore import TrustStore


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
    log.info("Finished signing manifest.")

    pstorename = Path(storename)
    with pstorename.open("w") as shandle:
        trust_store.to_json(shandle)
    log.info(f"🔐 Saved certificates/signatures into '{pstorename}'.")
