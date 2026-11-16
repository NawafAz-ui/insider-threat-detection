# SPEDIA in the CERT layout (prototype dataset)

Converted from: Álvarez, D., et al. (2025). *System for Prediction and Early Detection of Insider Attacks (SPEDIA) Dataset*, version 2. Zenodo. https://doi.org/10.5281/zenodo.15525713 (file `logs_SPEDIA_annotated_en.csv`, MD5 e01e0baaf3b523a0b493fc9c52af2b1c). Licence: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

Changes made: the events were reduced to the five CERT files with `python -m itd.spedia --map spedia_mapping.json`, sessions are built from 30-minute activity gaps, and shell commands, login records and events without a user were left out. Details: `docs/DATA_PREPARATION_SPEDIA.pdf`.
