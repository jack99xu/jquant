"""git 封装测试：在 tmp_path 构造临时 git 仓库验证（hermetic，不触碰真实仓库）。"""
import subprocess
from pathlib import Path

import pytest

from research import git_meta

HELLO_BLOB = "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0"  # git hash-object "hello"


def _make_repo(tmp_path: Path, content: str = "hello", message: str = "init") -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    f = root / "strategy.md"
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=root, check=True)
    return root


def test_commit_hash_length(tmp_path):
    root = _make_repo(tmp_path)
    assert len(git_meta.git_commit_hash(root)) == 40


def test_blob_hash_matches_known_value(tmp_path):
    root = _make_repo(tmp_path)
    assert git_meta.git_blob_hash(root, "strategy.md") == HELLO_BLOB


def test_worktree_clean_true_when_committed(tmp_path):
    root = _make_repo(tmp_path)
    assert git_meta.worktree_clean(root, "strategy.md") is True


def test_worktree_clean_false_after_edit(tmp_path):
    root = _make_repo(tmp_path)
    (root / "strategy.md").write_text("changed", encoding="utf-8")
    assert git_meta.worktree_clean(root, "strategy.md") is False


def test_commit_message(tmp_path):
    root = _make_repo(tmp_path, message="add strategy")
    assert git_meta.commit_message(root) == "add strategy"


def test_diff_between_shows_change(tmp_path):
    root = _make_repo(tmp_path)
    h1 = git_meta.git_commit_hash(root)
    (root / "strategy.md").write_text("hello world", encoding="utf-8")
    subprocess.run(["git", "add", "strategy.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "second"], cwd=root, check=True)
    h2 = git_meta.git_commit_hash(root)
    diff = git_meta.diff_between(root, h1, h2, "strategy.md")
    assert "+hello world" in diff


def test_git_error_raises(tmp_path):
    with pytest.raises(RuntimeError):
        git_meta.git_commit_hash(tmp_path)  # 非 git 仓库