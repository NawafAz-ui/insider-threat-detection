"""Unpack the five CERT event files from an official release archive (for example r4.2.tar.bz2),
keeping only the columns the engine reads (itd.ingest.FILES). The archive is read as a stream, so
the full release (the http file alone is several GB) is never unpacked on disk. The other files of
the release (readme, LDAP, psychometric) are copied unchanged to a reference folder.
   python scripts/extract_cert.py <archive> <dataset folder> <reference folder>
Writes extract_manifest.json (rows, kept and dropped columns, SHA-256 of each output) to the dataset folder."""
import bz2
import codecs
import csv
import hashlib
import json
import os
import shutil
import sys
import tarfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from itd.ingest import FILES  # noqa: E402

csv.field_size_limit(sys.maxsize)            # the content columns of http and email can be long


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def reduce_csv(src, dst, keep):
    """Copy the columns in keep, rows in their original order. latin-1 keeps every byte as it was."""
    rows = odd = 0
    reader = csv.reader(codecs.iterdecode(src, "latin-1"))   # a streamed member cannot seek, so no TextIOWrapper
    header = next(reader)
    idx = [header.index(c) for c in keep]    # ValueError if the release lacks a column
    with open(dst, "w", encoding="latin-1", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(keep)
        for row in reader:
            odd += len(row) != len(header)
            w.writerow([row[i] for i in idx])
            rows += 1
    return header, rows, odd


def main(archive, out, ref):
    os.makedirs(out, exist_ok=True)
    os.makedirs(ref, exist_ok=True)
    manifest = {"archive": os.path.basename(archive), "archive_sha256": sha256(archive), "files": {}, "reference_files": []}
    # bz2.open reads every bzip2 stream of the file. tarfile's own "r|bz2" stops after the first one,
    # and the CERT archives hold many streams.
    with bz2.open(archive, "rb") as raw, tarfile.open(fileobj=raw, mode="r|") as tar:
        for m in tar:
            if not m.isfile():
                continue
            name = os.path.basename(m.name)
            kind = name[:-4] if name.endswith(".csv") else None
            if kind in FILES:
                dst = os.path.join(out, name)
                header, rows, odd = reduce_csv(tar.extractfile(m), dst, FILES[kind])
                manifest["files"][name] = {
                    "source": m.name, "source_bytes": m.size, "source_columns": header, "kept_columns": FILES[kind],
                    "dropped_columns": [c for c in header if c not in FILES[kind]], "rows": rows,
                    "rows_with_other_field_count": odd, "bytes": os.path.getsize(dst), "sha256": sha256(dst)}
                print(f"{name}: {rows:,} rows, kept {', '.join(FILES[kind])}", flush=True)
                continue
            rel = os.path.normpath(m.name)
            if rel.startswith("..") or os.path.isabs(rel):
                continue                             # never write outside the reference folder
            dst = os.path.join(ref, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                shutil.copyfileobj(tar.extractfile(m), f)
            manifest["reference_files"].append(rel)
    missing = [f"{k}.csv" for k in FILES if f"{k}.csv" not in manifest["files"]]
    if missing:
        raise SystemExit(f"The archive has no {', '.join(missing)}")
    with open(os.path.join(out, "extract_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
