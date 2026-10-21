"""Module to ask the user how to set up the demo notebook's download"""

import logging
import sys
from pathlib import Path
from types import SimpleNamespace

IDX_BASE_URL = "https://locate-beta.ncbi.nlm.nih.gov/idx/v2/"
DRS_BASE_URL = "https://locate-beta.ncbi.nlm.nih.gov/ga4gh/drs/v1/"


def configure_download() -> SimpleNamespace:
    """Ask the user for information to configure the demo download

    Returns:
        A namespace containing the values used by the notebook's
        downloading code.
    """
    while True:
        data_source = input("Data source (dbGaP/SRA) [dbGaP]: ").strip().lower() or "dbgap"
        if data_source in {"dbgap", "sra"}:
            break
        print("Please enter dbGaP or SRA.")

    if data_source == "dbgap":
        source_prefix = "gap"
        default_accession = "phs000710"
    else:
        source_prefix = "sra"
        default_accession = "SRR21790641"

    accession = input(f"Accession [{default_accession}]: ").strip() or default_accession
    source = f"{source_prefix}/{accession}"

    passport_default = Path.home() / "passport-enc.txt"
    passport_input = input(f"Passport absolute path [{passport_default}]: ").strip()
    passport_path = Path(passport_input or passport_default).expanduser()
    if not passport_path.is_absolute():
        raise ValueError("The passport path must be absolute.")

    output_default = (Path.cwd() / source).resolve()
    output_input = input(f"Output directory absolute path [{output_default}]: ").strip()
    output_directory = Path(output_input or output_default).expanduser()
    if not output_directory.is_absolute():
        raise ValueError("The output directory path must be absolute.")
    output_directory.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    with passport_path.open("r") as passport_file:
        passport_text = passport_file.read().strip()

    passport_size_bytes = len(passport_text.encode("utf-8"))
    print("\nConfiguration and setup complete.")
    print(f"Study/source: {source}")
    print(f"Passport path: {passport_path}")
    print(f"Your output directory will be: {output_directory}")
    print(f"Your RAS passport was read successfully ({passport_size_bytes:,} bytes).")
    print("DRS and IDX API endpoints are ready.")

    return SimpleNamespace(
        source=source,
        output_directory=output_directory,
        passport_text=passport_text,
        idx_base_url=IDX_BASE_URL.rstrip("/"),
        drs_base_url=DRS_BASE_URL.rstrip("/"),
    )
