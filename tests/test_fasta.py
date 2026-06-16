"""Round-trip tests for the shared FASTA helpers (SC-006)."""

import os

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from biopytools.common import fasta
from biopytools.common.io import slugify


def _records():
    return [
        SeqRecord(Seq("ACGTACGT"), id="seq1", description="seq1 first"),
        SeqRecord(Seq("TTTTGGGG"), id="seq2", description="seq2 second"),
    ]


def test_write_then_read_round_trip(tmp_path):
    path = tmp_path / "out.fasta"
    n = fasta.write_records(_records(), str(path))
    assert n == 2

    back = fasta.read_records(str(path))
    assert [r.id for r in back] == ["seq1", "seq2"]
    assert str(back[0].seq) == "ACGTACGT"
    assert str(back[1].seq) == "TTTTGGGG"


def test_split_records_one_file_per_record(tmp_path):
    src = tmp_path / "multi.fasta"
    fasta.write_records(_records(), str(src))

    out_dir = tmp_path / "split"
    written = fasta.split_records(str(src), out_dir=str(out_dir))

    assert len(written) == 2
    assert os.path.isdir(out_dir)
    names = sorted(os.path.basename(p) for p in written)
    assert names == ["seq1.fasta", "seq2.fasta"]
    # Each split file holds exactly its one record.
    first = fasta.read_records(written[0])
    assert len(first) == 1


def test_split_sanitizes_record_id_filenames(tmp_path):
    src = tmp_path / "weird.fasta"
    # A FASTA id keeps everything up to the first space; use separators that
    # would be dangerous in a filename (pipe, slash, backslash).
    weird_id = "gi|123/abc\\x"
    rec = SeqRecord(Seq("ACGT"), id=weird_id, description=weird_id)
    fasta.write_records([rec], str(src))

    written = fasta.split_records(str(src), out_dir=str(tmp_path / "out"))
    assert len(written) == 1
    filename = os.path.basename(written[0])
    # No path separators leak into the filename (FR-008).
    assert filename == f"{slugify(weird_id)}.fasta"
    assert not any(sep in filename for sep in ("/", "\\", "|", " "))
