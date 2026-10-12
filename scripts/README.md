# OULAD preparation scripts

These scripts rebuild and inspect the day-63 modelling table documented in data/processed/. They expect the original OULAD CSV files in data/raw/ and use the dependency listed in requirements-data-prep.txt.

Run from the repository root:

    python scripts/build_oulad_day63.py
    python scripts/inspect_oulad.py
