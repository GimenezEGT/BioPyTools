"""Tests for the subprocess-based BLAST runners (no real BLAST+ required).

The Biopython 1.85 removal of ``Bio.Blast.Applications`` forced a switch to
direct ``subprocess`` calls; these tests lock that behaviour by monkeypatching
``shutil.which`` and ``subprocess.run`` so they run anywhere.
"""

import subprocess

import pytest

from biopytools.common.blast import header_line
from biopytools.qpcr import blast_primers
from biopytools.blast import blastn


def _fake_run_writing_output(returncode=0, data_line="q1\tHomo sapiens\n"):
    """Return a fake ``subprocess.run`` that writes the ``-out`` file."""
    def _run(command, capture_output=False, text=False):
        out_path = command[command.index("-out") + 1]
        if returncode == 0:
            with open(out_path, "w") as handle:
                handle.write(data_line)
        return subprocess.CompletedProcess(command, returncode, stdout="",
                                           stderr="" if returncode == 0 else "boom")
    return _run


def test_run_blast_missing_executable(monkeypatch, tmp_path):
    monkeypatch.setattr(blast_primers.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError):
        blast_primers.run_blast("q.fasta", str(tmp_path / "out"))


def test_run_blast_success_inserts_header(monkeypatch, tmp_path):
    monkeypatch.setattr(blast_primers.shutil, "which", lambda name: "/usr/bin/blastn")
    monkeypatch.setattr(blast_primers.subprocess, "run",
                        _fake_run_writing_output(returncode=0))

    out = blast_primers.run_blast("q.fasta", str(tmp_path / "out"),
                                  num_alignments=10)

    assert out == str(tmp_path / "out.tsv")
    with open(out) as handle:
        first_line = handle.readline().rstrip("\n")
    # Header derived from the shared field list is prepended (FR-011).
    assert first_line == header_line()


def test_run_blast_nonzero_exit_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(blast_primers.shutil, "which", lambda name: "/usr/bin/blastn")
    monkeypatch.setattr(blast_primers.subprocess, "run",
                        _fake_run_writing_output(returncode=2))
    with pytest.raises(RuntimeError):
        blast_primers.run_blast("q.fasta", str(tmp_path / "out"))


def test_run_blastn_builds_remote_command(monkeypatch, tmp_path):
    """blast.blastn passes -remote by default and inserts the shared header."""
    monkeypatch.setattr(blastn.shutil, "which", lambda name: "/usr/bin/blastn")
    captured = {}

    def _capture(command, capture_output=False, text=False):
        captured["command"] = command
        with open(command[command.index("-out") + 1], "w") as handle:
            handle.write("q1\tHomo sapiens\n")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(blastn.subprocess, "run", _capture)
    out = blastn.run_blastn("q.fasta", str(tmp_path / "out"), remote=True)

    assert "-remote" in captured["command"]
    assert "-outfmt" in captured["command"]
    with open(out) as handle:
        assert handle.readline().rstrip("\n") == header_line()
