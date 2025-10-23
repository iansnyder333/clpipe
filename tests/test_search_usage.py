from __future__ import annotations

from pathlib import Path

from tools.search_usage import UsageMatch, search_usage_in_repo


def test_search_usage_in_repo_basic(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("first line\nsecond pkg_resource line\n")
    (tmp_path / "b.txt").write_text("Pkg_RESOURCE appears here\n")
    ignored_dir = tmp_path / "build"
    ignored_dir.mkdir()
    (ignored_dir / "ignored.txt").write_text("pkg_resource should not be found\n")

    matches = search_usage_in_repo("pkg_resource", root=tmp_path)

    assert matches == [
        UsageMatch(path=Path("a.txt"), line_number=2, line_text="second pkg_resource line"),
    ]


def test_search_usage_in_repo_case_insensitive(tmp_path: Path) -> None:
    (tmp_path / "c.txt").write_text("Pkg_RESOURCE appears here\n")

    matches = search_usage_in_repo("pkg_resource", root=tmp_path, case_sensitive=False)

    assert matches == [
        UsageMatch(path=Path("c.txt"), line_number=1, line_text="Pkg_RESOURCE appears here"),
    ]
